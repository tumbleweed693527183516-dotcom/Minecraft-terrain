package com.vividlands.village;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Vec3i;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

/**
 * A standalone site (stave church, mead hall, thing site, fishing hamlet...): one template on dry,
 * gentle ground. Sites that need the sea or a lake ("min_water") are placed beside it and turned
 * so their front (the -z side, where a jetty runs out) faces the water.
 */
public class SiteStructure extends Structure {
    public static final Codec<SiteStructure> CODEC = RecordCodecBuilder.create(i -> i.group(
            settingsCodec(i),
            ResourceLocation.CODEC.listOf().fieldOf("templates").forGetter(s -> s.templates),
            Codec.INT.optionalFieldOf("sink", 0).forGetter(s -> s.sink),
            Codec.INT.optionalFieldOf("max_slope", 10).forGetter(s -> s.maxSlope),
            Codec.INT.optionalFieldOf("min_water", 0).forGetter(s -> s.minWater)
    ).apply(i, SiteStructure::new));

    private final List<ResourceLocation> templates;
    private final int sink, maxSlope, minWater;

    public SiteStructure(StructureSettings settings, List<ResourceLocation> templates, int sink, int maxSlope,
                         int minWater) {
        super(settings);
        this.templates = templates;
        this.sink = sink;
        this.maxSlope = maxSlope;
        this.minWater = minWater;
    }

    @Override
    public StructureType<?> type() {
        return ModStructures.SITE;
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
        RandomSource rand = ctx.random();
        ResourceLocation id = templates.get(rand.nextInt(templates.size()));
        Vec3i size = ctx.structureTemplateManager().getOrCreate(id).getSize();
        int cx = ctx.chunkPos().getMiddleBlockX(), cz = ctx.chunkPos().getMiddleBlockZ();
        int half = Math.max(size.getX(), size.getZ()) / 2;
        Rotation rot = Rotation.getRandom(rand);
        if (minWater > 0) {
            // look around for open water and face it
            int found = 0;
            double sx = 0, sz = 0;
            for (int i = 0; i < 16; i++) {
                double a = i * Math.PI / 8;
                for (int r : new int[]{half + 6, half + 16}) {
                    int x = (int) Math.round(cx + Math.cos(a) * r), z = (int) Math.round(cz + Math.sin(a) * r);
                    if (VikingVillageStructure.isWater(ctx, x, VikingVillageStructure.height(ctx, x, z), z)) {
                        found++;
                        sx += Math.cos(a);
                        sz += Math.sin(a);
                    }
                }
            }
            if (found < minWater) {
                return Optional.empty();
            }
            rot = VikingVillageStructure.Planner.faceToward(cx, cz, (int) Math.round(cx + sx * 100),
                    (int) Math.round(cz + sz * 100));
        }
        // the footprint itself must be dry and fairly level
        int inner = Math.max(2, Math.min(size.getX(), size.getZ()) / 2 - 2);
        int[] ys = new int[9];
        int n = 0, wet = 0;
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                int x = cx + dx * inner, z = cz + dz * inner;
                int y = VikingVillageStructure.height(ctx, x, z);
                if (VikingVillageStructure.isWater(ctx, x, y, z)) {
                    if (dx == 0 && dz == 0) {
                        return Optional.empty();
                    }
                    wet++;
                }
                ys[n++] = y;
            }
        }
        int[] sorted = ys.clone();
        Arrays.sort(sorted);
        // ignore the single highest and lowest sample (a boulder, a creek bed)
        if (wet > (minWater > 0 ? 3 : 1) || sorted[7] - sorted[1] > maxSlope) {
            return Optional.empty();
        }
        int y = sorted[4] - sink;
        Rotation finalRot = rot;
        return Optional.of(new GenerationStub(new BlockPos(cx, y, cz), builder ->
                builder.addPiece(new SitePiece(ctx.structureTemplateManager(), id, cx, y, cz, finalRot))));
    }
}
