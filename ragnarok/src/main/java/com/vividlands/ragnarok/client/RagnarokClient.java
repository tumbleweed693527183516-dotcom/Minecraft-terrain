package com.vividlands.ragnarok.client;

import net.fabricmc.api.ClientModInitializer;

public class RagnarokClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        if (Boolean.getBoolean("vividlands.rendertest")) {
            RenderTest.install();          // only in the automatic render test (gradle runRenderTest)
        }
    }
}
