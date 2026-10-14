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

/**
 * Grades a village site before anything is built: inside the wall the ground becomes a level
 * plateau at the village's ground height (hills cut away, hollows and ponds filled), and a smooth
 * skirt outside blends the plateau back into the natural land. Uses the local surface blocks so
 * the result looks natural. Added as the first piece so every building lands on finished ground.
 */
public class GradePiece extends StructurePiece {
    static final int SKIRT = 16;
    private final VikingVillageStructure.Ring ring;
    private final int groundY, margin;

    GradePiece(VikingVillageStructure.Ring ring, int groundY, int margin) {
        super(ModStructures.GRADE_PIECE, 0, box(ring, groundY, margin));
        this.ring = ring;
        this.groundY = groundY;
        this.margin = margin;
    }

    public GradePiece(CompoundTag tag) {
        super(ModStructures.GRADE_PIECE, tag);
        this.ring = new VikingVillageStructure.Ring(tag.getInt("CX"), tag.getInt("CZ"), tag.getDouble("R"),
                tag.getDouble("A1"), tag.getDouble("P1"), tag.getDouble("A2"), tag.getDouble("P2"));
        this.groundY = tag.getInt("GY");
        this.margin = tag.getInt("M");
    }

    private static BoundingBox box(VikingVillageStructure.Ring ring, int groundY, int margin) {
        int r = (int) Math.ceil(ring.radius * 1.12) + margin + SKIRT + 1;
        return new BoundingBox(ring.cx - r, groundY - 48, ring.cz - r, ring.cx + r, groundY + 72, ring.cz + r);
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
        tag.putInt("GY", groundY);
        tag.putInt("M", margin);
    }

    /** How strongly (0..1) the ground at (x, z) is pulled to the village level. */
    static double weight(VikingVillageStructure.Ring ring, int margin, double x, double z) {
        double d = Math.hypot(x - ring.cx, z - ring.cz);
        double t = (d - (ring.radiusAt(ring.angleOf(x, z)) + margin)) / SKIRT;
        if (t <= 0) {
            return 1;
        }
        if (t >= 1) {
            return 0;
        }
        return 1 - t * t * (3 - 2 * t);
    }

    static int graded(int raw, int groundY, double w) {
        return (int) Math.round(raw + (groundY - raw) * w);
    }

    private static boolean soil(BlockState s) {
        return s.is(BlockTags.DIRT) || s.is(BlockTags.SAND) || s.is(Blocks.GRAVEL) || s.is(Blocks.SNOW_BLOCK)
                || s.is(Blocks.MUD) || s.is(Blocks.CLAY) || s.is(ModBlocks.BLACK_SAND) || s.is(ModBlocks.PEAT)
                || s.is(ModBlocks.VOLCANIC_ASH);
    }

    private static boolean clutter(BlockState s) {
        return !s.isAir() && (s.is(BlockTags.LOGS) || s.is(BlockTags.LEAVES) || !s.isSolid()
                || s.is(Blocks.SNOW) || s.is(Blocks.BAMBOO) || s.is(Blocks.MOSS_CARPET));
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager structureManager, ChunkGenerator generator,
                            RandomSource random, BoundingBox chunkBox, ChunkPos chunkPos, BlockPos pivot) {
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        BlockState air = Blocks.AIR.defaultBlockState();
        BlockState dirt = Blocks.DIRT.defaultBlockState();
        int x0 = Math.max(boundingBox.minX(), chunkBox.minX()), x1 = Math.min(boundingBox.maxX(), chunkBox.maxX());
        int z0 = Math.max(boundingBox.minZ(), chunkBox.minZ()), z1 = Math.min(boundingBox.maxZ(), chunkBox.maxZ());
        for (int x = x0; x <= x1; x++) {
            for (int z = z0; z <= z1; z++) {
                double w = weight(ring, margin, x + 0.5, z + 0.5);
                if (w <= 0.001) {
                    continue;
                }
                // find the real ground (skipping trees, plants and snow), and any water on top of it
                int top = Integer.MIN_VALUE, waterTop = Integer.MIN_VALUE;
                boolean snowy = false;
                for (int y = groundY + 70; y > groundY - 46; y--) {
                    p.set(x, y, z);
                    BlockState s = level.getBlockState(p);
                    if (s.is(Blocks.SNOW)) {
                        snowy = true;
                    }
                    if (!s.getFluidState().isEmpty()) {
                        if (waterTop == Integer.MIN_VALUE) {
                            waterTop = y;
                        }
                        continue;
                    }
                    if (!s.isAir() && !clutter(s)) {
                        top = y;
                        break;
                    }
                }
                if (top == Integer.MIN_VALUE) {
                    continue;
                }
                if (waterTop != Integer.MIN_VALUE && w < 0.5) {
                    continue;                                  // leave lake and sea shores outside alone
                }
                p.set(x, top, z);
                BlockState surface = level.getBlockState(p);
                p.set(x, top - 1, z);
                BlockState under = level.getBlockState(p);
                if (waterTop != Integer.MIN_VALUE || !soil(surface)) {
                    surface = w > 0.5 ? Blocks.GRASS_BLOCK.defaultBlockState() : surface;
                }
                if (surface.is(Blocks.GRASS_BLOCK) || surface.is(Blocks.PODZOL) || surface.is(Blocks.MYCELIUM)) {
                    under = dirt;
                } else if (!soil(under)) {
                    under = surface.is(BlockTags.SAND) ? surface : dirt;
                }
                int g = graded(top, groundY, w);
                // fill up (also replaces pond water), or cut down
                for (int y = top + 1; y <= g; y++) {
                    p.set(x, y, z);
                    level.setBlock(p, y == g ? surface : under, 2);
                }
                if (g < top) {
                    p.set(x, g, z);
                    level.setBlock(p, surface, 2);
                }
                // clear everything above the new ground: cut earth, trees, plants, water
                boolean full = w >= 0.98;
                int clearTo = Math.max(top, waterTop) + (full || Math.abs(g - top) >= 2 ? 34 : 2);
                for (int y = g + 1; y <= clearTo; y++) {
                    p.set(x, y, z);
                    BlockState s = level.getBlockState(p);
                    if (s.isAir()) {
                        continue;
                    }
                    if (y <= top || full || clutter(s) || !s.getFluidState().isEmpty()) {
                        level.setBlock(p, air, 2);
                    }
                }
                if (snowy || surface.is(Blocks.SNOW_BLOCK)) {           // put the snow cover back
                    p.set(x, g + 1, z);
                    if (level.getBlockState(p).isAir()) {
                        level.setBlock(p, Blocks.SNOW.defaultBlockState(), 2);
                    }
                }
            }
        }
    }
}
