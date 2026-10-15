package com.vividlands.village;

import net.fabricmc.api.ModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Vivid Lands: Vikings - an add-on for Vivid Lands. Walled Viking villages (replacing vanilla
 * villages), ring fortresses, burial mounds, ship burials, stave churches, mead halls, ships and
 * more. Without it, Vivid Lands generates vanilla structures.
 */
public class VividLandsVikings implements ModInitializer {
    public static final Logger LOG = LoggerFactory.getLogger("Vivid Lands: Vikings");

    @Override
    public void onInitialize() {
        ModStructures.init();
        LOG.info("Vivid Lands: Vikings ready");
    }
}
