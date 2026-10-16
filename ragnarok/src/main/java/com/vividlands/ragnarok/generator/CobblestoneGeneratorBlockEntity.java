/*
 * This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was
 * not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
 *
 * Ported from Kibe's BlockGeneratorBlockEntity by lucaargolo (https://github.com/lucaargolo/kibe, MPL-2.0).
 */
package com.vividlands.ragnarok.generator;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.Container;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.WorldlyContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BaseContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

public class CobblestoneGeneratorBlockEntity extends BaseContainerBlockEntity implements WorldlyContainer {
    private static final int SIZE = 27;
    private static final int[] SLOTS = java.util.stream.IntStream.range(0, SIZE).toArray();
    private final NonNullList<ItemStack> items = NonNullList.withSize(SIZE, ItemStack.EMPTY);
    private float progress;

    public CobblestoneGeneratorBlockEntity(BlockPos pos, BlockState state) {
        super(Generators.BLOCK_ENTITY, pos, state);
    }

    public static void tick(Level level, BlockPos pos, BlockState state, CobblestoneGeneratorBlockEntity be) {
        if (!(state.getBlock() instanceof CobblestoneGeneratorBlock generator)) return;
        be.progress += generator.rate;
        if (be.progress < 1f) return;
        int count = Mth.floor(be.progress);
        be.progress -= count;
        int left = count;
        for (int i = 0; i < SIZE && left > 0; i++) {
            ItemStack slot = be.items.get(i);
            if (slot.isEmpty()) {
                int n = Math.min(left, 64);
                be.items.set(i, new ItemStack(Items.COBBLESTONE, n));
                left -= n;
            } else if (slot.is(Items.COBBLESTONE) && slot.getCount() < slot.getMaxStackSize()) {
                int n = Math.min(left, slot.getMaxStackSize() - slot.getCount());
                slot.grow(n);
                left -= n;
            }
        }
        if (left == count) {
            be.progress = 0f;            // full: wait until something is taken out
        } else {
            be.setChanged();
        }
    }

    @Override
    protected Component getDefaultName() {
        return getBlockState().getBlock().getName();
    }

    @Override
    protected AbstractContainerMenu createMenu(int id, Inventory inventory) {
        return ChestMenu.threeRows(id, inventory, this);
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        items.clear();
        ContainerHelper.loadAllItems(tag, items);
        progress = tag.getFloat("progress");
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        ContainerHelper.saveAllItems(tag, items);
        tag.putFloat("progress", progress);
    }

    @Override
    public int getContainerSize() {
        return SIZE;
    }

    @Override
    public boolean isEmpty() {
        return items.stream().allMatch(ItemStack::isEmpty);
    }

    @Override
    public ItemStack getItem(int slot) {
        return items.get(slot);
    }

    @Override
    public ItemStack removeItem(int slot, int amount) {
        ItemStack out = ContainerHelper.removeItem(items, slot, amount);
        if (!out.isEmpty()) setChanged();
        return out;
    }

    @Override
    public ItemStack removeItemNoUpdate(int slot) {
        return ContainerHelper.takeItem(items, slot);
    }

    @Override
    public void setItem(int slot, ItemStack stack) {
        items.set(slot, stack);
        if (stack.getCount() > getMaxStackSize()) stack.setCount(getMaxStackSize());
        setChanged();
    }

    @Override
    public boolean stillValid(Player player) {
        return Container.stillValidBlockEntity(this, player);
    }

    @Override
    public void clearContent() {
        items.clear();
    }

    @Override
    public boolean canPlaceItem(int slot, ItemStack stack) {
        return false;                    // output only: hoppers and pipes can't fill it
    }

    @Override
    public int[] getSlotsForFace(Direction side) {
        return SLOTS;
    }

    @Override
    public boolean canPlaceItemThroughFace(int slot, ItemStack stack, @Nullable Direction side) {
        return false;
    }

    @Override
    public boolean canTakeItemThroughFace(int slot, ItemStack stack, Direction side) {
        return true;
    }
}
