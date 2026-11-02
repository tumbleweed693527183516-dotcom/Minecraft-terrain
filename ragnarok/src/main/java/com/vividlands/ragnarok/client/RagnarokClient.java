package com.vividlands.ragnarok.client;

import net.fabricmc.api.ClientModInitializer;

public class RagnarokClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        BossClient.init();
        ClassClient.init();
        // the Norse skin for the quest book (Odyssey Quests), on by default, can be turned off in Resource Packs
        net.fabricmc.loader.api.FabricLoader.getInstance().getModContainer(com.vividlands.ragnarok.Ragnarok.MOD_ID).ifPresent(mod ->
                net.fabricmc.fabric.api.resource.ResourceManagerHelper.registerBuiltinResourcePack(
                        new net.minecraft.resources.ResourceLocation(com.vividlands.ragnarok.Ragnarok.MOD_ID, "norse_quest_book"), mod,
                        net.minecraft.network.chat.Component.literal("Vivid Lands: Norse quest book"),
                        net.fabricmc.fabric.api.resource.ResourcePackActivationType.DEFAULT_ENABLED));
        NorseBossBar.init();
        com.vividlands.ragnarok.classes.RuneStoneItem.clientLevel = i -> ClassClient.levels[i];
        com.vividlands.ragnarok.armor.ArmorTraits.clientWearer = () -> net.minecraft.client.Minecraft.getInstance().player;
        net.fabricmc.fabric.api.client.item.v1.ItemTooltipCallback.EVENT.register((stack, context, lines) -> {
            com.vividlands.ragnarok.armor.Glamour.addTooltip(stack, lines);
            NorseTooltip.trophyLine(stack, lines);
        });
        if (Boolean.getBoolean("vividlands.rendertest")) {
            RenderTest.install();          // only in the automatic render test (gradle runRenderTest)
        }
    }
}
