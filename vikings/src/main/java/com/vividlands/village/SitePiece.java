package com.vividlands.village;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Vec3i;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.TemplateStructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.levelgen.structure.templatesystem.JigsawReplacementProcessor;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;

/** A site template placed as-is (terrain is smoothed by the structure's terrain adaptation). */
public class SitePiece extends TemplateStructurePiece {
    private final Rotation rotation;

    public SitePiece(StructureTemplateManager manager, ResourceLocation id, int centreX, int y, int centreZ,
                     Rotation rotation) {
        super(ModStructures.SITE_PIECE, 0, manager, id, id.toString(), settings(manager, id, rotation),
                origin(manager, id, centreX, y, centreZ));
        this.rotation = rotation;
    }

    public SitePiece(StructureTemplateManager manager, CompoundTag tag) {
        super(ModStructures.SITE_PIECE, tag, manager,
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
}
