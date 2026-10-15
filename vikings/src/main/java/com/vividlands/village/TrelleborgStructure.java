package com.vividlands.village;

import com.mojang.serialization.Codec;
import net.minecraft.world.level.levelgen.structure.StructureType;

/**
 * A Trelleborg-type ring fortress: a perfectly round earthen rampart topped by a palisade with a
 * ditch outside, four gates on the compass points joined by cross streets, and garrison halls
 * set out in ordered rows in the four quarters.
 */
public class TrelleborgStructure extends VikingVillageStructure {
    public static final Codec<TrelleborgStructure> CODEC = simpleCodec(TrelleborgStructure::new);

    public TrelleborgStructure(StructureSettings settings) {
        super(settings, VillageStyle.NORTH);
    }

    @Override
    protected boolean fortress() {
        return true;
    }

    @Override
    public StructureType<?> type() {
        return ModStructures.TRELLEBORG;
    }
}
