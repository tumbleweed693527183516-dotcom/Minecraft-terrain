package com.vividlands.village;

import com.vividlands.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

import java.util.ArrayList;
import java.util.List;

/** One arc of the village palisade: sharpened logs standing on the real ground, column by column. */
public class PalisadePiece extends StructurePiece {
    private final VikingVillageStructure.Ring ring;
    private final double a0, a1;
    private final int groundY;
    private final List<int[]> gates;

    PalisadePiece(VikingVillageStructure.Ring ring, double a0, double a1, List<int[]> gates, int groundY) {
        super(ModStructures.PALISADE_PIECE, 0, box(ring, a0, a1, groundY));
        this.ring = ring;
        this.a0 = a0;
        this.a1 = a1;
        this.gates = gates;
        this.groundY = groundY;
    }

    public PalisadePiece(CompoundTag tag) {
        super(ModStructures.PALISADE_PIECE, tag);
        this.ring = new VikingVillageStructure.Ring(tag.getInt("CX"), tag.getInt("CZ"), tag.getDouble("R"),
                tag.getDouble("A1"), tag.getDouble("P1"), tag.getDouble("A2"), tag.getDouble("P2"));
        this.a0 = tag.getDouble("S0");
        this.a1 = tag.getDouble("S1");
        this.groundY = tag.getInt("GY");
        this.gates = new ArrayList<>();
        int[] g = tag.getIntArray("Gates");
        for (int i = 0; i + 1 < g.length; i += 2) {
            gates.add(new int[]{g[i], g[i + 1]});
        }
    }

    private static BoundingBox box(VikingVillageStructure.Ring ring, double a0, double a1, int groundY) {
        int minX = Integer.MAX_VALUE, minZ = Integer.MAX_VALUE, maxX = Integer.MIN_VALUE, maxZ = Integer.MIN_VALUE;
        for (int i = 0; i <= 16; i++) {
            double a = a0 + (a1 - a0) * i / 16;
            double r = ring.radiusAt(a);
            int x = (int) Math.floor(ring.cx + Math.cos(a) * r), z = (int) Math.floor(ring.cz + Math.sin(a) * r);
            minX = Math.min(minX, x - 2);
            maxX = Math.max(maxX, x + 2);
            minZ = Math.min(minZ, z - 2);
            maxZ = Math.max(maxZ, z + 2);
        }
        return new BoundingBox(minX, groundY - 24, minZ, maxX, groundY + 30, maxZ);
    }

    @Override
    protected void addAdditionalSaveData(StructurePieceSerializationContext context, CompoundTag tag) {
        tag.putInt("CX", ring.cx);
        tag.putInt("CZ", ring.cz);
        tag.putDouble("R", ring.radius);
        tag.putDouble("A1", ring.a1);
        tag.putDouble("P1", ring.p1);
        tag.putDouble("A2", ring.a2);
        tag.putDouble("P2", ring.p2);
        tag.putDouble("S0", a0);
        tag.putDouble("S1", a1);
        tag.putInt("GY", groundY);
        int[] g = new int[gates.size() * 2];
        for (int i = 0; i < gates.size(); i++) {
            g[i * 2] = gates.get(i)[0];
            g[i * 2 + 1] = gates.get(i)[1];
        }
        tag.putIntArray("Gates", g);
    }

    static boolean isGround(BlockState s) {
        return !s.isAir() && s.getFluidState().isEmpty() && s.isSolid() && !s.is(BlockTags.LOGS)
                && !s.is(BlockTags.LEAVES);
    }

    static int findGround(WorldGenLevel level, int x, int z, int hint) {
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int y = hint + 28; y > hint - 24; y--) {
            p.set(x, y, z);
            BlockState s = level.getBlockState(p);
            if (!s.getFluidState().isEmpty()) {
                return -(y + 1000);                 // water surface (negative marks water)
            }
            if (isGround(s)) {
                return y;
            }
        }
        return hint;
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager structureManager, ChunkGenerator generator,
                            RandomSource random, BoundingBox chunkBox, ChunkPos chunkPos, BlockPos pivot) {
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        BlockState log = Blocks.SPRUCE_LOG.defaultBlockState();
        BlockState dark = Blocks.STRIPPED_SPRUCE_LOG.defaultBlockState();
        BlockState stake = ModBlocks.PALISADE_STAKE.defaultBlockState();
        for (int x = Math.max(boundingBox.minX(), chunkBox.minX()); x <= Math.min(boundingBox.maxX(), chunkBox.maxX()); x++) {
            for (int z = Math.max(boundingBox.minZ(), chunkBox.minZ()); z <= Math.min(boundingBox.maxZ(), chunkBox.maxZ()); z++) {
                double cxp = x + 0.5, czp = z + 0.5;
                double ang = ring.angleOf(cxp, czp);
                if (ang < a0 || ang >= a1) {
                    continue;
                }
                double d = Math.hypot(cxp - ring.cx, czp - ring.cz);
                double r = ring.radiusAt(ang);
                if (d < r - 0.55 || d >= r + 0.65) {
                    continue;
                }
                boolean nearGate = false;
                for (int[] g : gates) {
                    if (Math.hypot(x - g[0], z - g[1]) < 8.6) {
                        nearGate = true;
                        break;
                    }
                }
                if (nearGate) {
                    continue;
                }
                int g = findGround(level, x, z, groundY);
                int base = g < -500 ? -g - 1000 - 3 : g;        // in water: start from the bed below
                long hash = (long) x * 73428767L ^ (long) z * 912931L;
                int height = 4 + (int) ((hash >>> 7) & 1);
                for (int y = base + 1; y <= base + height; y++) {
                    p.set(x, y, z);
                    level.setBlock(p, (hash >>> 11 & 3) == 0 ? dark : log, 2);
                }
                p.set(x, base + height + 1, z);
                level.setBlock(p, stake, 2);
                // fill under the wall so it never floats on a slope
                for (int y = base; y > base - 8; y--) {
                    p.set(x, y, z);
                    BlockState s = level.getBlockState(p);
                    if (isGround(s)) {
                        break;
                    }
                    level.setBlock(p, log, 2);
                }
            }
        }
    }
}
