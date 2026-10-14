package com.vividlands.village;

import com.vividlands.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
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

import java.util.Set;

/** Village paths: worn dirt, gravel and coarse dirt laid on the real ground; plank bridges over water. */
public class PathPiece extends StructurePiece {
    private final long[] cells;
    private final int groundY;

    PathPiece(Set<Long> cells, int groundY) {
        super(ModStructures.PATH_PIECE, 0, box(cells, groundY));
        this.cells = cells.stream().mapToLong(Long::longValue).toArray();
        this.groundY = groundY;
    }

    public PathPiece(CompoundTag tag) {
        super(ModStructures.PATH_PIECE, tag);
        this.cells = tag.getLongArray("Cells");
        this.groundY = tag.getInt("GY");
    }

    private static BoundingBox box(Set<Long> cells, int groundY) {
        int minX = Integer.MAX_VALUE, minZ = Integer.MAX_VALUE, maxX = Integer.MIN_VALUE, maxZ = Integer.MIN_VALUE;
        for (long c : cells) {
            int x = (int) (c >> 32), z = (int) c;
            minX = Math.min(minX, x);
            maxX = Math.max(maxX, x);
            minZ = Math.min(minZ, z);
            maxZ = Math.max(maxZ, z);
        }
        if (cells.isEmpty()) {
            return new BoundingBox(0, groundY, 0, 0, groundY, 0);
        }
        return new BoundingBox(minX, groundY - 24, minZ, maxX, groundY + 30, maxZ);
    }

    @Override
    protected void addAdditionalSaveData(StructurePieceSerializationContext context, CompoundTag tag) {
        tag.putLongArray("Cells", cells);
        tag.putInt("GY", groundY);
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager structureManager, ChunkGenerator generator,
                            RandomSource random, BoundingBox chunkBox, ChunkPos chunkPos, BlockPos pivot) {
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (long c : cells) {
            int x = (int) (c >> 32), z = (int) c;
            if (x < chunkBox.minX() || x > chunkBox.maxX() || z < chunkBox.minZ() || z > chunkBox.maxZ()) {
                continue;
            }
            int g = PalisadePiece.findGround(level, x, z, groundY);
            long hash = (long) x * 341873128712L + (long) z * 132897987541L;
            int pick = (int) ((hash >>> 16) % 10 + 10) % 10;
            if (g < -500) {
                p.set(x, -g - 1000, z);
                level.setBlock(p, Blocks.SPRUCE_PLANKS.defaultBlockState(), 2);
                continue;
            }
            p.set(x, g, z);
            BlockState here = level.getBlockState(p);
            if (!(here.is(Blocks.GRASS_BLOCK) || here.is(Blocks.DIRT) || here.is(Blocks.COARSE_DIRT)
                    || here.is(Blocks.PODZOL) || here.is(Blocks.SAND) || here.is(Blocks.GRAVEL)
                    || here.is(Blocks.SNOW_BLOCK) || here.is(Blocks.MOSS_BLOCK) || here.is(Blocks.MUD)
                    || here.is(Blocks.ROOTED_DIRT) || here.is(Blocks.MYCELIUM) || here.is(ModBlocks.BLACK_SAND)
                    || here.is(ModBlocks.PEAT) || here.is(ModBlocks.VOLCANIC_ASH) || here.is(Blocks.TUFF)
                    || here.is(Blocks.BLACKSTONE))) {
                continue;     // don't pave over stone floors, foundations or rock
            }
            BlockState surface = pick < 6 ? Blocks.DIRT_PATH.defaultBlockState()
                    : pick < 8 ? Blocks.GRAVEL.defaultBlockState() : Blocks.COARSE_DIRT.defaultBlockState();
            level.setBlock(p, surface, 2);
            for (int y = g + 1; y <= g + 2; y++) {
                p.set(x, y, z);
                BlockState above = level.getBlockState(p);
                if (!above.isAir() && above.canBeReplaced()) {
                    level.setBlock(p, Blocks.AIR.defaultBlockState(), 2);
                }
            }
        }
    }
}
