package com.vividlands.village;


import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;

public final class ModStructures {
    public static final StructureType<VikingVillageStructure> VIKING_VILLAGE = Registry.register(
            BuiltInRegistries.STRUCTURE_TYPE, id("viking_village"), () -> VikingVillageStructure.CODEC);
    public static final StructureType<TrelleborgStructure> TRELLEBORG = Registry.register(
            BuiltInRegistries.STRUCTURE_TYPE, id("trelleborg"), () -> TrelleborgStructure.CODEC);

    public static final StructureType<SiteStructure> SITE = Registry.register(
            BuiltInRegistries.STRUCTURE_TYPE, id("site"), () -> SiteStructure.CODEC);

    public static final StructurePieceType SITE_PIECE = Registry.register(BuiltInRegistries.STRUCTURE_PIECE,
            id("site_template"), (StructurePieceType.StructureTemplateType) SitePiece::new);
    public static final StructurePieceType TEMPLATE_PIECE = Registry.register(BuiltInRegistries.STRUCTURE_PIECE,
            id("village_template"), (StructurePieceType.StructureTemplateType) TemplatePiece::new);
    public static final StructurePieceType PALISADE_PIECE = Registry.register(BuiltInRegistries.STRUCTURE_PIECE,
            id("village_palisade"), (StructurePieceType.ContextlessType) PalisadePiece::new);
    public static final StructurePieceType GRADE_PIECE = Registry.register(BuiltInRegistries.STRUCTURE_PIECE,
            id("village_grade"), (StructurePieceType.ContextlessType) GradePiece::new);
    public static final StructurePieceType PATH_PIECE = Registry.register(BuiltInRegistries.STRUCTURE_PIECE,
            id("village_path"), (StructurePieceType.ContextlessType) PathPiece::new);

    private ModStructures() {
    }

    private static ResourceLocation id(String path) {
        return new ResourceLocation("vividlands", path);
    }

    public static void init() {
        // touching this class registers everything above
    }
}
