package com.vividlands;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.util.KeyDispatchDataCodec;
import net.minecraft.world.level.levelgen.DensityFunction;

import java.util.HashMap;
import java.util.Map;

/**
 * Density function "vividlands:terrain_2d": the whole Vivid Lands land shape in one step.
 *
 * Basin-and-range mountains (warped range belts, crest ridges, side spurs, horn summits),
 * real-world mountain stamps, the squashed vanilla base and the creek network were
 * originally written as ~60 data-driven density functions. Referenced from many places,
 * that tree was copied and re-indexed for every chunk and every structure height check,
 * which cost about a fifth of generation time. Here it is computed once per block column
 * (per thread) and shared by the three outputs:
 *
 *   mode "offset"            terrain height offset (vanilla offset + mountains, carved by creeks)
 *   mode "mountain_presence" 0..1, how mountainous a column is (cave entrances, biomes)
 *   mode "biome_erosion"     erosion as the biome map sees it (mountain biomes follow the ranges)
 *
 * The maths mirrors tools/generate.py exactly; constants come from the data file.
 */
public record Terrain2D(String mode, Map<String, DensityFunction.NoiseHolder> noises, Map<String, Double> params,
                        DensityFunction offset, DensityFunction erosion, DensityFunction continents,
                        DensityFunction ridges, DensityFunction stamps) implements DensityFunction {

    private static final MapCodec<Terrain2D> MAP_CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            Codec.STRING.fieldOf("mode").forGetter(Terrain2D::mode),
            Codec.unboundedMap(Codec.STRING, DensityFunction.NoiseHolder.CODEC).fieldOf("noises").forGetter(Terrain2D::noises),
            Codec.unboundedMap(Codec.STRING, Codec.DOUBLE).fieldOf("params").forGetter(Terrain2D::params),
            DensityFunction.HOLDER_HELPER_CODEC.fieldOf("offset").forGetter(Terrain2D::offset),
            DensityFunction.HOLDER_HELPER_CODEC.fieldOf("erosion").forGetter(Terrain2D::erosion),
            DensityFunction.HOLDER_HELPER_CODEC.fieldOf("continents").forGetter(Terrain2D::continents),
            DensityFunction.HOLDER_HELPER_CODEC.fieldOf("ridges").forGetter(Terrain2D::ridges),
            DensityFunction.HOLDER_HELPER_CODEC.fieldOf("stamps").forGetter(Terrain2D::stamps)
    ).apply(i, Terrain2D::new));
    public static final KeyDispatchDataCodec<Terrain2D> CODEC = KeyDispatchDataCodec.of(MAP_CODEC);

    /** Last column computed on this thread; shared by all three modes of the same world. */
    private static final class Column {
        Object key;
        int x = Integer.MIN_VALUE, z = Integer.MIN_VALUE;
        double offset, presence, erosion;
    }

    private static final ThreadLocal<Column> LAST = ThreadLocal.withInitial(Column::new);

    private DensityFunction.NoiseHolder n(String name) {
        return noises.get(name);
    }

    private double p(String name) {
        return params.get(name);
    }

    private static double clamp(double v, double lo, double hi) {
        return v < lo ? lo : (v > hi ? hi : v);
    }

    private static double oneMinusAbs(double v, double scale) {
        return clamp(1.0 - scale * Math.abs(v), 0.0, 1.0);
    }

    /** shifted_noise with xz_scale 1, y_scale 0 and shifts taken from two warp noises. */
    private static double warped(DensityFunction.NoiseHolder noise, double x, double z, double sx, double sz) {
        return noise.getValue(x + sx, 0.0, z + sz);
    }

    @Override
    public double compute(FunctionContext ctx) {
        Column c = column(ctx);
        return switch (mode) {
            case "mountain_presence" -> c.presence;
            case "biome_erosion" -> c.erosion;
            default -> c.offset;
        };
    }

    private Column column(FunctionContext ctx) {
        int bx = ctx.blockX(), bz = ctx.blockZ();
        Column c = LAST.get();
        Object key = n("mountain_range_belts").noise();      // one instance per world (RandomState)
        if (c.x == bx && c.z == bz && c.key == key && key != null) {
            return c;
        }
        double x = bx, z = bz;

        // ---- mountains (generate.py: mountains()) ----
        double warp = p("warp_blocks");
        double wx = warp * n("mountain_warp_x").getValue(x, 0, z);
        double wz = warp * n("mountain_warp_z").getValue(x, 0, z);
        double axis = oneMinusAbs(warped(n("mountain_range_belts"), x, z, wx, wz), 1.0 / p("range_width"));
        double foot = 1.0 - axis;
        double front = 1.0 - foot * foot * foot;
        double crest = axis * axis;
        double ridgeBase = oneMinusAbs(warped(n("mountain_ridges"), x, z, wx, wz), 1.0);
        double ridge = ridgeBase * ridgeBase;
        double detailBase = oneMinusAbs(warped(n("mountain_ridges_detail"), x, z, wx, wz), 1.0);
        double ridgeDetail = detailBase * detailBase * clamp(2.0 * ridge, 0.0, 1.0);
        double hornBase = clamp(oneMinusAbs(warped(n("mountain_horn_a"), x, z, wx, wz), 1.0)
                * oneMinusAbs(warped(n("mountain_horn_b"), x, z, wx, wz), 1.0), 0.0, 1.0);
        double horn = (hornBase * hornBase) * (hornBase * hornBase);
        double size = clamp(0.75 + 0.6 * n("mountain_massif").getValue(x, 0, z), 0.4, 1.0);
        double shape = p("range_body")
                + p("range_crest") * crest * (0.5 + 0.5 * ridge)
                + p("range_side_ridges") * ridgeDetail * axis
                + p("horn_peaks") * horn * crest;
        double ero = erosion.compute(ctx);
        double rugged = clamp(0.9 - 1.3 * ero, 0.0, 1.0);
        double inland = clamp(3.0 * (continents.compute(ctx) + 0.05), 0.0, 1.0);
        double presence = rugged * inland * front;
        double gorge = clamp(8.0 * (Math.abs(ridges.compute(ctx)) - 0.03), 0.0, 1.0);
        double procedural = presence * gorge * size * shape;
        double stampRegion = clamp(1.2 - 1.3 * ero, 0.0, 1.0) * inland;
        double stamp = stampRegion > 0 ? stampRegion * stamps.compute(ctx) : 0.0;
        double height = Math.max(procedural, stamp);
        double mountainPresence = Math.max(presence, clamp(2.5 * (stamp - 0.08), 0.0, 1.0));

        // ---- land: vanilla shape squashed above a soft cap, plus the mountains ----
        double van = offset.compute(ctx);
        double cap = p("base_soft_cap");
        double land = Math.min(van, cap) + p("base_soft_keep") * Math.max(van - cap, 0.0) + height;

        // ---- creeks (generate.py: creeks()) ----
        double carved = land;
        double lowland = clamp(-6.0 * (land - p("creek_max_offset")), 0.0, 1.0);
        double above = Math.max(land - p("creek_floor"), 0.0);
        if (lowland > 0 && above > 0) {
            double cwx = 40.0 * n("creek_warp_x").getValue(x, 0, z);
            double cwz = 40.0 * n("creek_warp_z").getValue(x, 0, z);
            double creek = clamp(2.0 * (1.0 - Math.abs(warped(n("creek_network"), x, z, cwx, cwz)) / p("creek_width")),
                    0.0, 1.0);
            double brook = 0.85 * clamp(2.0 * (1.0 - Math.abs(warped(n("brook_network"), x, z, cwx, cwz))
                    / p("brook_width")), 0.0, 1.0);
            carved = land - Math.max(creek, brook) * lowland * above;
        }

        c.key = key;
        c.x = bx;
        c.z = bz;
        c.offset = carved;
        c.presence = mountainPresence;
        c.erosion = Math.max(ero, -0.2) - 2.0 * mountainPresence;
        return c;
    }

    @Override
    public void fillArray(double[] values, ContextProvider provider) {
        provider.fillAllDirectly(values, this);
    }

    @Override
    public DensityFunction mapAll(Visitor visitor) {
        Map<String, DensityFunction.NoiseHolder> mapped = new HashMap<>();
        noises.forEach((k, v) -> mapped.put(k, visitor.visitNoise(v)));
        return visitor.apply(new Terrain2D(mode, mapped, params, offset.mapAll(visitor), erosion.mapAll(visitor),
                continents.mapAll(visitor), ridges.mapAll(visitor), stamps.mapAll(visitor)));
    }

    @Override
    public double minValue() {
        return -16.0;
    }

    @Override
    public double maxValue() {
        return 16.0;
    }

    @Override
    public KeyDispatchDataCodec<? extends DensityFunction> codec() {
        return CODEC;
    }
}
