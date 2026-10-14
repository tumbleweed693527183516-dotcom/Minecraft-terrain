package com.vividlands;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class VividLands implements ModInitializer {
    public static final String MOD_ID = "vividlands";
    public static final Logger LOG = LoggerFactory.getLogger("Vivid Lands");

    @Override
    public void onInitialize() {
        ModBlocks.init();
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, new ResourceLocation(MOD_ID, "main"),
                FabricItemGroup.builder()
                        .title(Component.translatable("itemGroup.vividlands"))
                        .icon(() -> new ItemStack(ModBlocks.PALM_LOG))
                        .displayItems((params, output) -> ModBlocks.ALL.forEach(output::accept))
                        .build());
        StampLibrary.load();
        Registry.register(BuiltInRegistries.DENSITY_FUNCTION_TYPE, new ResourceLocation(MOD_ID, "stamps"),
                StampDensity.CODEC.codec());
        LOG.info("Vivid Lands ready: {} blocks", ModBlocks.ALL.size());
    }
}
