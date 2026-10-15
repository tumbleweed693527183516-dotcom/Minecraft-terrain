package com.vividlands;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.blockrenderlayer.v1.BlockRenderLayerMap;
import net.fabricmc.fabric.api.client.rendering.v1.ColorProviderRegistry;
import net.minecraft.client.renderer.BiomeColors;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.world.level.FoliageColor;
import net.minecraft.world.level.block.Block;

public class VividLandsClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        BlockRenderLayerMap.INSTANCE.putBlocks(RenderType.cutout(), ModBlocks.CUTOUT.toArray(new Block[0]));
        BlockRenderLayerMap.INSTANCE.putBlocks(RenderType.cutoutMipped(), ModBlocks.CUTOUT_MIPPED.toArray(new Block[0]));
        // Leaves use Minecraft's own (grey) leaf textures, tinted like vanilla leaves:
        // palms follow the biome foliage colour, pines and redwoods keep evergreen shades.
        ColorProviderRegistry.BLOCK.register((state, level, pos, tint) -> level != null && pos != null
                ? BiomeColors.getAverageFoliageColor(level, pos) : FoliageColor.getDefaultColor(), ModBlocks.PALM_LEAVES);
        ColorProviderRegistry.BLOCK.register((state, level, pos, tint) -> 0x5E8C4F, ModBlocks.PINE_LEAVES);
        ColorProviderRegistry.BLOCK.register((state, level, pos, tint) -> 0x46703A, ModBlocks.REDWOOD_LEAVES);
        ColorProviderRegistry.ITEM.register((stack, tint) -> FoliageColor.getDefaultColor(), ModBlocks.PALM_LEAVES);
        ColorProviderRegistry.ITEM.register((stack, tint) -> 0x5E8C4F, ModBlocks.PINE_LEAVES);
        ColorProviderRegistry.ITEM.register((stack, tint) -> 0x46703A, ModBlocks.REDWOOD_LEAVES);
    }
}
