package com.vividlands.ragnarok.client;

import com.vividlands.ragnarok.Ragnarok;
import com.vividlands.ragnarok.armor.VikingArmor;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.item.ItemStack;

/** Norse tooltip frame for every item of the pack's own mod; boss trophies get a blood-red border. */
public final class NorseTooltip {
    private NorseTooltip() {
    }

    public static ItemStack current = ItemStack.EMPTY;

    /** Boss trophies say which boss they came from. */
    public static void trophyLine(ItemStack stack, java.util.List<net.minecraft.network.chat.Component> lines) {
        String id = BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
        for (var d : com.vividlands.ragnarok.boss.Bosses.DEFS.values()) {
            if (id.equals(d.firstDrop())) {
                lines.add(1, net.minecraft.network.chat.Component.literal("Trophy of ")
                        .append(net.minecraft.network.chat.Component.translatable(d.nameKey()))
                        .withStyle(st -> st.withColor(0xE07A66)));
                return;
            }
        }
    }

    public static boolean draw(GuiGraphics g, int x, int y, int w, int h, int z) {
        if (current.isEmpty() || !Ragnarok.MOD_ID.equals(BuiltInRegistries.ITEM.getKey(current.getItem()).getNamespace())) return false;
        int border = VikingArmor.TROPHIES.contains(current.getItem()) ? NorseUI.BLOOD : NorseUI.BRONZE;
        NorseUI.panel(g, x - 3, y - 3, w + 6, h + 6, border, 0xF5141A22, z);
        return true;
    }
}
