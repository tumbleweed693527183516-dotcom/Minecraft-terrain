package com.vividlands;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Blocks from the mods Vivid Lands builds with (it has no blocks of its own):
 * Oh The Biomes We've Gone (biomeswevegone) and Decorative Blocks (decorative_blocks).
 * Looked up by id at world-generation time, so there is no compile-time dependency.
 */
public final class ModCompat {
    public static final String BWG = "biomeswevegone";
    public static final String DB = "decorative_blocks";

    private ModCompat() {
    }

    public static Block block(String namespace, String path, Block fallback) {
        ResourceLocation id = new ResourceLocation(namespace, path);
        return BuiltInRegistries.BLOCK.containsKey(id) ? BuiltInRegistries.BLOCK.get(id) : fallback;
    }

    public static BlockState state(String namespace, String path, Block fallback) {
        return block(namespace, path, fallback).defaultBlockState();
    }

    /** Soil-like mod blocks the village grader and paths may treat as natural ground. */
    public static boolean isModSoil(BlockState s) {
        ResourceLocation id = BuiltInRegistries.BLOCK.getKey(s.getBlock());
        if (!BWG.equals(id.getNamespace())) {
            return false;
        }
        String p = id.getPath();
        return p.endsWith("_sand") || p.equals("peat") || p.equals("dacite") || p.startsWith("lush_")
                || p.startsWith("sandy_") || p.equals("white_sandstone");
    }

    /** A sharpened-log palisade (Decorative Blocks) in the given vanilla wood. */
    public static BlockState palisade(String wood) {
        return state(DB, wood + "_palisade", Blocks.SPRUCE_FENCE);
    }
}
