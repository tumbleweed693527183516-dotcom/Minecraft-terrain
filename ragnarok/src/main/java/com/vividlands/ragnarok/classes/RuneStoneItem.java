package com.vividlands.ragnarok.classes;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** A class's rune stone: use it to switch to that class. Every class keeps its own level. */
public class RuneStoneItem extends Item {
    private final NorseClass cls;
    /** Your level in a class (by ordinal), set by the client for the tooltip. */
    public static java.util.function.IntUnaryOperator clientLevel = i -> 0;

    public RuneStoneItem(NorseClass cls, Properties properties) {
        super(properties);
        this.cls = cls;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player instanceof ServerPlayer sp) {
            Classes.setClass(sp, cls);
            player.getCooldowns().addCooldown(this, 40);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    @Override
    public Component getName(ItemStack stack) {
        return super.getName(stack).copy().withStyle(st -> st.withColor(cls.color));
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> lines, TooltipFlag flag) {
        int lv = clientLevel.applyAsInt(cls.ordinal());
        lines.add(Component.literal("Use to walk this path" + (lv > 0 ? " · your level " + lv : "")).withStyle(ChatFormatting.GRAY));
        lines.add(Component.literal(cls.passive + ": " + cls.passiveText).withStyle(ChatFormatting.GRAY));
        for (NorseClass.Ability a : cls.abilities) {
            boolean open = lv >= a.unlock();
            lines.add(Component.literal("Lv " + a.unlock() + "  ").withStyle(open ? ChatFormatting.GOLD : ChatFormatting.DARK_GRAY)
                    .append(Component.literal(a.name()).withStyle(open ? ChatFormatting.WHITE : ChatFormatting.DARK_GRAY)));
        }
    }
}
