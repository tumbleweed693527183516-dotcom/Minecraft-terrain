/*
 * This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was
 * not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
 *
 * Cobblestone Generators ported from Kibe by lucaargolo (https://github.com/lucaargolo/kibe, MPL-2.0):
 * same tiers, rates, recipes and textures. Only the cobblestone generator is taken from Kibe.
 */
package com.vividlands.ragnarok.generator;

import com.vividlands.ragnarok.Ragnarok;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;

public final class Generators {
    private static final Block[] LOOKS = {Blocks.IRON_BLOCK, Blocks.GOLD_BLOCK, Blocks.DIAMOND_BLOCK,
            Blocks.EMERALD_BLOCK, Blocks.NETHERITE_BLOCK};
    public static final CobblestoneGeneratorBlock[] BLOCKS = new CobblestoneGeneratorBlock[5];
    public static BlockEntityType<CobblestoneGeneratorBlockEntity> BLOCK_ENTITY;

    private Generators() {
    }

    public static void register() {
        float rate = 0.01f;                       // MK1: 0.2 cobblestone per second, x4 per tier
        for (int tier = 1; tier <= 5; tier++, rate *= 4f) {
            ResourceLocation id = new ResourceLocation(Ragnarok.MOD_ID, "cobblestone_generator_mk" + tier);
            CobblestoneGeneratorBlock block = new CobblestoneGeneratorBlock(
                    BlockBehaviour.Properties.copy(LOOKS[tier - 1]).lightLevel(s -> 4), tier, rate);
            BLOCKS[tier - 1] = Registry.register(BuiltInRegistries.BLOCK, id, block);
            Registry.register(BuiltInRegistries.ITEM, id, new BlockItem(block, new Item.Properties()));
        }
        BLOCK_ENTITY = Registry.register(BuiltInRegistries.BLOCK_ENTITY_TYPE,
                new ResourceLocation(Ragnarok.MOD_ID, "cobblestone_generator"),
                BlockEntityType.Builder.of(CobblestoneGeneratorBlockEntity::new, BLOCKS).build(null));
        ItemGroupEvents.modifyEntriesEvent(CreativeModeTabs.FUNCTIONAL_BLOCKS).register(entries -> {
            for (Block b : BLOCKS) entries.accept(b);
        });
    }
}
