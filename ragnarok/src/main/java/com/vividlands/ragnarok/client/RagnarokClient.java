package com.vividlands.ragnarok.client;

import net.fabricmc.api.ClientModInitializer;

public class RagnarokClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        BossClient.init();
        ClassClient.init();
        NorseBossBar.init();
        com.vividlands.ragnarok.classes.RuneStoneItem.clientLevel = i -> ClassClient.levels[i];
        com.vividlands.ragnarok.armor.ArmorTraits.clientWearer = () -> net.minecraft.client.Minecraft.getInstance().player;
        net.fabricmc.fabric.api.client.item.v1.ItemTooltipCallback.EVENT.register((stack, context, lines) ->
                com.vividlands.ragnarok.armor.Glamour.addTooltip(stack, lines));
        if (Boolean.getBoolean("vividlands.rendertest")) {
            RenderTest.install();          // only in the automatic render test (gradle runRenderTest)
        }
    }
}
