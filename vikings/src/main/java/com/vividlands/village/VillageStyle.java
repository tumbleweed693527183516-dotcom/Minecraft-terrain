package com.vividlands.village;


import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Regional looks for Viking villages, so every vanilla village type has a Norse counterpart:
 * north (turf and spruce, the homeland), snow (dark timber, snow roofs), forest (oak halls),
 * steppe (birch Rus towns), desert (Varangian trading posts in palm wood and sandstone) and
 * jungle (far-voyager camps in jungle wood). Buildings are pre-built per style by
 * tools/structures; this holds the pieces the Java generator lays itself.
 */
public enum VillageStyle {
    NORTH("north"), SNOW("snow"), FOREST("forest"), STEPPE("steppe"), DESERT("desert"), JUNGLE("jungle");

    public final String id;

    VillageStyle(String id) {
        this.id = id;
    }

    public static VillageStyle of(String id) {
        for (VillageStyle s : values()) {
            if (s.id.equals(id)) {
                return s;
            }
        }
        return NORTH;
    }

    BlockState wallLog() {
        return switch (this) {
            case SNOW, STEPPE -> Blocks.DARK_OAK_LOG.defaultBlockState();
            case FOREST -> Blocks.OAK_LOG.defaultBlockState();
            case DESERT -> ModCompat.state(ModCompat.BWG, "palm_log", Blocks.ACACIA_LOG);
            case JUNGLE -> Blocks.JUNGLE_LOG.defaultBlockState();
            default -> Blocks.SPRUCE_LOG.defaultBlockState();
        };
    }

    /** Decorative Blocks palisade wood for the sharpened tops of the wall. */
    String palisadeWood() {
        return switch (this) {
            case SNOW, STEPPE -> "dark_oak";
            case FOREST -> "oak";
            case DESERT -> "acacia";
            case JUNGLE -> "jungle";
            default -> "spruce";
        };
    }

    BlockState wallAccent() {
        return switch (this) {
            case SNOW, STEPPE -> Blocks.STRIPPED_DARK_OAK_LOG.defaultBlockState();
            case FOREST -> Blocks.STRIPPED_OAK_LOG.defaultBlockState();
            case DESERT -> Blocks.STRIPPED_ACACIA_LOG.defaultBlockState();
            case JUNGLE -> Blocks.STRIPPED_JUNGLE_LOG.defaultBlockState();
            default -> Blocks.STRIPPED_SPRUCE_LOG.defaultBlockState();
        };
    }

    /** Path surface for a hash pick 0..9. */
    BlockState path(int pick) {
        if (this == DESERT) {
            return pick < 5 ? Blocks.SMOOTH_SANDSTONE.defaultBlockState()
                    : pick < 8 ? Blocks.GRAVEL.defaultBlockState() : Blocks.PACKED_MUD.defaultBlockState();
        }
        if (this == SNOW) {
            return pick < 5 ? Blocks.DIRT_PATH.defaultBlockState()
                    : pick < 8 ? Blocks.GRAVEL.defaultBlockState() : Blocks.PACKED_ICE.defaultBlockState();
        }
        return pick < 6 ? Blocks.DIRT_PATH.defaultBlockState()
                : pick < 8 ? Blocks.GRAVEL.defaultBlockState() : Blocks.COARSE_DIRT.defaultBlockState();
    }

    BlockState bridge() {
        return switch (this) {
            case FOREST -> Blocks.OAK_PLANKS.defaultBlockState();
            case STEPPE -> Blocks.BIRCH_PLANKS.defaultBlockState();
            case DESERT -> Blocks.ACACIA_PLANKS.defaultBlockState();
            case JUNGLE -> Blocks.JUNGLE_PLANKS.defaultBlockState();
            case SNOW -> Blocks.DARK_OAK_PLANKS.defaultBlockState();
            default -> Blocks.SPRUCE_PLANKS.defaultBlockState();
        };
    }
}
