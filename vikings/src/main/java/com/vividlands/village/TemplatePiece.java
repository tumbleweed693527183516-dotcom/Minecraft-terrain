package com.vividlands.village;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Vec3i;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.TemplateStructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.levelgen.structure.templatesystem.JigsawReplacementProcessor;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;

/**
 * A building template placed at ground level. Before the template goes down, the footprint is
 * cleared of terrain and trees above the floor and filled solid below it, so buildings sit
 * cleanly on slopes without hovering or being buried.
 */
public class TemplatePiece extends TemplateStructurePiece {
    private final Rotation rotation;

    public TemplatePiece(StructureTemplateManager manager, ResourceLocation id, int centreX, int y, int centreZ,
                         Rotation rotation) {
        super(ModStructures.TEMPLATE_PIECE, 0, manager, id, id.toString(), settings(manager, id, rotation),
                origin(manager, id, centreX, y, centreZ));
        this.rotation = rotation;
    }

    public TemplatePiece(StructureTemplateManager manager, CompoundTag tag) {
        super(ModStructures.TEMPLATE_PIECE, tag, manager,
                id -> settings(manager, id, Rotation.valueOf(tag.getString("Rot"))));
        this.rotation = Rotation.valueOf(tag.getString("Rot"));
    }

    private static StructurePlaceSettings settings(StructureTemplateManager manager, ResourceLocation id, Rotation rot) {
        Vec3i size = manager.getOrCreate(id).getSize();
        return new StructurePlaceSettings().setRotation(rot)
                .setRotationPivot(new BlockPos(size.getX() / 2, 0, size.getZ() / 2))
                .addProcessor(JigsawReplacementProcessor.INSTANCE);
    }

    private static BlockPos origin(StructureTemplateManager manager, ResourceLocation id, int cx, int y, int cz) {
        Vec3i size = manager.getOrCreate(id).getSize();
        return new BlockPos(cx - size.getX() / 2, y, cz - size.getZ() / 2);
    }

    @Override
    protected void addAdditionalSaveData(StructurePieceSerializationContext context, CompoundTag tag) {
        super.addAdditionalSaveData(context, tag);
        tag.putString("Rot", rotation.name());
    }

    @Override
    protected void handleDataMarker(String marker, BlockPos pos, ServerLevelAccessor level, RandomSource random,
                                    BoundingBox box) {
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager structureManager, ChunkGenerator generator,
                            RandomSource random, BoundingBox chunkBox, ChunkPos chunkPos, BlockPos pivot) {
        BoundingBox bb = this.boundingBox;
        int floor = this.templatePosition.getY();
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        BlockState fill = Blocks.DIRT.defaultBlockState();
        for (int x = Math.max(bb.minX(), chunkBox.minX()); x <= Math.min(bb.maxX(), chunkBox.maxX()); x++) {
            for (int z = Math.max(bb.minZ(), chunkBox.minZ()); z <= Math.min(bb.maxZ(), chunkBox.maxZ()); z++) {
                for (int y = floor + 1; y <= bb.maxY() + 2; y++) {
                    p.set(x, y, z);
                    if (!level.getBlockState(p).isAir()) {
                        level.setBlock(p, Blocks.AIR.defaultBlockState(), 2);
                    }
                }
                for (int y = floor - 1; y > floor - 16; y--) {
                    p.set(x, y, z);
                    BlockState s = level.getBlockState(p);
                    if (s.isSolid() && s.getFluidState().isEmpty()) {
                        break;
                    }
                    level.setBlock(p, y == floor - 1 ? Blocks.COBBLESTONE.defaultBlockState() : fill, 2);
                }
            }
        }
        super.postProcess(level, structureManager, generator, random, chunkBox, chunkPos, pivot);
    }
}
