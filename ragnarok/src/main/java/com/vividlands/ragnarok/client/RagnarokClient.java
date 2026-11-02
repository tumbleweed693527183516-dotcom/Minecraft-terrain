package com.vividlands.ragnarok.client;

import net.fabricmc.api.ClientModInitializer;

public class RagnarokClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        BossClient.init();
        ClassClient.init();
        net.fabricmc.fabric.api.client.item.v1.ItemTooltipCallback.EVENT.register((stack, context, lines) ->
                com.vividlands.ragnarok.armor.Glamour.addTooltip(stack, lines));
        if (Boolean.getBoolean("vividlands.rendertest")) {
            RenderTest.install();          // only in the automatic render test (gradle runRenderTest)
        }
    }
}
