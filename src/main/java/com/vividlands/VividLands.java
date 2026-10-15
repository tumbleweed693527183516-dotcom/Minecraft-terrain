package com.vividlands;

import net.fabricmc.api.ModInitializer;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class VividLands implements ModInitializer {
    public static final String MOD_ID = "vividlands";
    public static final Logger LOG = LoggerFactory.getLogger("Vivid Lands");

    @Override
    public void onInitialize() {
        com.vividlands.village.ModStructures.init();
        StampLibrary.load();
        Registry.register(BuiltInRegistries.DENSITY_FUNCTION_TYPE, new ResourceLocation(MOD_ID, "stamps"),
                StampDensity.CODEC.codec());
        LOG.info("Vivid Lands ready (building with Oh The Biomes We've Gone and Decorative Blocks)");
    }
}
