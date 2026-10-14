package com.vividlands;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.util.KeyDispatchDataCodec;
import net.minecraft.world.level.levelgen.DensityFunction;

import java.util.List;

/**
 * Density function "vividlands:stamps": places real-world mountains into the world.
 *
 * The world is split into square cells. Each cell may hold one stamp, picked, rotated,
 * mirrored, scaled and positioned by a hash of the cell and the world seed (the seed
 * reaches us through {@code seed_noise}, which Minecraft seeds per world). Output is
 * height in Vivid Lands depth units, 0 outside stamps; edges are feathered in the data.
 */
public record StampDensity(DensityFunction.NoiseHolder seedNoise, int cellSize, double chance,
                           double scaleMin, double scaleMax) implements DensityFunction {

    private static final MapCodec<StampDensity> MAP_CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            DensityFunction.NoiseHolder.CODEC.fieldOf("seed_noise").forGetter(StampDensity::seedNoise),
            Codec.INT.fieldOf("cell_size").forGetter(StampDensity::cellSize),
            Codec.DOUBLE.fieldOf("chance").forGetter(StampDensity::chance),
            Codec.DOUBLE.optionalFieldOf("scale_min", 0.85).forGetter(StampDensity::scaleMin),
            Codec.DOUBLE.optionalFieldOf("scale_max", 1.15).forGetter(StampDensity::scaleMax)
    ).apply(i, StampDensity::new));
    public static final KeyDispatchDataCodec<StampDensity> CODEC = KeyDispatchDataCodec.of(MAP_CODEC);

    @Override
    public double compute(FunctionContext ctx) {
        return sample(ctx.blockX(), ctx.blockZ());
    }

    @Override
    public void fillArray(double[] values, ContextProvider provider) {
        provider.fillAllDirectly(values, this);
    }

    @Override
    public DensityFunction mapAll(Visitor visitor) {
        return visitor.apply(new StampDensity(visitor.visitNoise(seedNoise), cellSize, chance, scaleMin, scaleMax));
    }

    @Override
    public double minValue() {
        return 0;
    }

    @Override
    public double maxValue() {
        return StampLibrary.maxHeight() * 1.15;
    }

    @Override
    public KeyDispatchDataCodec<? extends DensityFunction> codec() {
        return CODEC;
    }

    private double sample(int x, int z) {
        List<StampLibrary.Stamp> stamps = StampLibrary.all();
        if (stamps.isEmpty()) {
            return 0;
        }
        int cx = Math.floorDiv(x, cellSize), cz = Math.floorDiv(z, cellSize);
        long h = cellHash(cx, cz);
        if (unit(h, 0) >= chance) {
            return 0;
        }
        StampLibrary.Stamp s = stamps.get(Math.min((int) (unit(h, 1) * stamps.size()), stamps.size() - 1));
        double scale = scaleMin + (scaleMax - scaleMin) * unit(h, 2);
        double blocksPerPx = s.blocksPerPx() * scale;
        double half = (s.size() - 1) * blocksPerPx / 2;
        double margin = Math.max(0, cellSize / 2.0 - half);
        double centerX = (double) cx * cellSize + cellSize / 2.0 + (unit(h, 3) * 2 - 1) * margin;
        double centerZ = (double) cz * cellSize + cellSize / 2.0 + (unit(h, 4) * 2 - 1) * margin;
        double dx = x + 0.5 - centerX, dz = z + 0.5 - centerZ;
        if (dx * dx + dz * dz > half * half) {
            return 0;
        }
        double angle = unit(h, 5) * Math.PI * 2;
        double cos = Math.cos(angle), sin = Math.sin(angle);
        double rx = dx * cos + dz * sin, rz = -dx * sin + dz * cos;
        if (unit(h, 6) < 0.5) {
            rx = -rx;
        }
        double centerPx = (s.size() - 1) / 2.0;
        double height = s.sample(rx / blocksPerPx + centerPx, rz / blocksPerPx + centerPx);
        return height * s.heightUnits() * (0.9 + 0.2 * unit(h, 7));
    }

    private long cellHash(int cx, int cz) {
        double n = seedNoise.getValue(cx * 1.731 + 0.37, 0, cz * 1.917 + 0.53);
        long bits = Double.doubleToLongBits(n);
        return mix(bits ^ (cx * 0x9E3779B97F4A7C15L) ^ (cz * 0xC2B2AE3D27D4EB4FL));
    }

    private static double unit(long h, int k) {
        return (mix(h + k * 0x9E3779B97F4A7C15L) >>> 11) * 0x1.0p-53;
    }

    private static long mix(long z) {
        z = (z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L;
        z = (z ^ (z >>> 27)) * 0x94D049BB133111EBL;
        return z ^ (z >>> 31);
    }
}
