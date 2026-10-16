package com.vividlands.ragnarok;

import net.fabricmc.api.ModInitializer;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.Level;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Vivid Lands: Ragnarok, the modpack's own mod.
 *
 * Pack rules (mixins in com.vividlands.ragnarok.mixin):
 *  - no Warden: sculk shriekers never summon one (they still shriek and give Darkness)
 *  - the Nether is closed: obsidian frames never light, nothing travels there
 *  - the End is closed: eyes of ender can't be placed in portal frames, nothing travels there
 * Everything those dimensions give is made with Create instead (data/vividlands_ragnarok/recipes).
 */
public class Ragnarok implements ModInitializer {
    public static final String MOD_ID = "vividlands_ragnarok";
    public static final Logger LOG = LoggerFactory.getLogger(MOD_ID);

    public static boolean closed(ResourceKey<Level> dimension) {
        return dimension == Level.NETHER || dimension == Level.END;
    }

    @Override
    public void onInitialize() {
        LOG.info("Vivid Lands: Ragnarok - Warden disabled, Nether and End closed");
    }
}
