package com.vividlands.ragnarok.client;

import com.vividlands.ragnarok.classes.Classes;
import com.vividlands.ragnarok.classes.NorseClass;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.toasts.Toast;
import net.minecraft.client.gui.components.toasts.ToastComponent;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/** The Norse pop-up in the top right: framed slate, an icon, a gold title and one line. */
public class NorseToast implements Toast {
    private final ItemStack icon;
    private final Component title, line;
    private final int border, titleColor;

    NorseToast(ItemStack icon, Component title, Component line, int border, int titleColor) {
        this.icon = icon;
        this.title = title;
        this.line = line;
        this.border = border;
        this.titleColor = titleColor;
    }

    static NorseToast levelUp(NorseClass c, int level, String unlocked) {
        Component line = unlocked.isEmpty() ? Component.literal("Your abilities grow stronger")
                : Component.literal("New ability: " + unlocked);
        return new NorseToast(new ItemStack(Classes.RUNES.get(c)), Component.literal(c.title + " level " + level), line,
                NorseUI.BRONZE, NorseUI.GOLD);
    }

    private static final String[] DIRS = {"south", "south-west", "west", "north-west", "north", "north-east", "east", "south-east"};

    static NorseToast beast(String boss, int dx, int dz) {
        String dir = DIRS[Math.floorMod(Math.round((float) (Math.toDegrees(Math.atan2(-dx, dz)) / 45.0)), 8)];
        int dist = (int) Math.round(Math.sqrt((double) dx * dx + (double) dz * dz));
        ItemStack icon = trophy(boss);
        return new NorseToast(icon, Component.literal("A great beast stirs nearby"),
                Component.translatable("entity.vividlands_ragnarok." + boss).append(" · " + dist + " blocks " + dir),
                NorseUI.BLOOD, 0xFFE07A66);
    }

    private static ItemStack trophy(String boss) {
        var def = com.vividlands.ragnarok.boss.Bosses.byId(boss);
        if (def != null && def.firstDrop() != null) {
            var item = BuiltInRegistries.ITEM.get(new ResourceLocation(def.firstDrop()));
            if (item != Items.AIR) return new ItemStack(item);
        }
        return new ItemStack(Items.BONE);
    }

    @Override
    public int width() {
        return 200;
    }

    @Override
    public Visibility render(GuiGraphics g, ToastComponent toasts, long time) {
        NorseUI.panel(g, 2, 2, width() - 4, height() - 4, border, 0xF2182029);
        g.renderItem(icon, 8, 8);
        g.drawString(toasts.getMinecraft().font, title, 30, 8, titleColor, false);
        g.drawString(toasts.getMinecraft().font, toasts.getMinecraft().font.plainSubstrByWidth(line.getString(), width() - 36), 30, 19, 0xFFC9D4DE, false);
        return time >= 5000L ? Visibility.HIDE : Visibility.SHOW;
    }
}
