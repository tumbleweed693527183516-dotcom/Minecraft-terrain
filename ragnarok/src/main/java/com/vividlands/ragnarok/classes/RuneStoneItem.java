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
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> lines, TooltipFlag flag) {
        lines.add(Component.literal("Use to become a " + cls.title).withStyle(s -> s.withColor(cls.color)));
        lines.add(Component.literal(cls.passive + ": " + cls.passiveText).withStyle(ChatFormatting.GRAY));
        for (NorseClass.Ability a : cls.abilities) {
            lines.add(Component.literal("Lv " + a.unlock() + "  " + a.name()).withStyle(ChatFormatting.DARK_AQUA));
        }
    }
}
