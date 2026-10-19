package com.vividlands.ragnarok.loot;

import net.fabricmc.fabric.api.loot.v2.LootTableEvents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;

import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * The Nether and End are closed, so treasure that only their chests (fortresses, bastions, End cities) would give is
 * moved into Overworld treasure chests instead: Too Many Bows' uncraftable bows and charms. Items of mods that aren't
 * installed are skipped.
 */
public final class ClosedRealmLoot {
    private static final String TMB = "too_many_bows:";
    private static final List<String> ITEMS = List.of(
            "aethers_call", "ancient_sage_bow", "arc_heavens", "arcane_bow", "arcforge", "astral_bound", "auroras_grace",
            "burnt_relic", "cyroheart_bow", "dark_bow", "demons_grasp", "dragons_breath", "emerald_sage_bow", "flame_bow",
            "scatter_bow", "solar_bow", "spectral_whisper", "tidal_bow", "torchbearer", "verdant_viper", "vitality_weaver",
            "webstring", "wind_bow", "dead_eyes_pendant", "fletchers_talisman", "sharpshot_ring", "stormbound_signet",
            "wind_glove");
    /** chest -> chance that one of the items is in it */
    private static final Set<String> RARE = Set.of("minecraft:chests/simple_dungeon", "minecraft:chests/abandoned_mineshaft",
            "minecraft:chests/pillager_outpost", "minecraft:chests/shipwreck_treasure");
    private static final Set<String> GOOD = Set.of("minecraft:chests/stronghold_corridor", "minecraft:chests/stronghold_library",
            "minecraft:chests/ancient_city", "minecraft:chests/jungle_temple", "minecraft:chests/desert_pyramid",
            "minecraft:chests/woodland_mansion", "minecraft:chests/buried_treasure");

    private ClosedRealmLoot() {
    }

    public static void register() {
        LootTableEvents.MODIFY.register((resources, loot, id, table, source) -> {
            if (!source.isBuiltin()) return;
            String key = id.toString();
            float chance = GOOD.contains(key) ? 0.25f : RARE.contains(key) ? 0.08f : 0f;
            if (chance == 0f) return;
            LootPool.Builder pool = LootPool.lootPool().setRolls(ConstantValue.exactly(1))
                    .when(LootItemRandomChanceCondition.randomChance(chance));
            int n = 0;
            for (String name : ITEMS) {
                Optional<Item> item = BuiltInRegistries.ITEM.getOptional(new ResourceLocation(TMB + name));
                if (item.isPresent()) {
                    pool.add(LootItem.lootTableItem(item.get()));
                    n++;
                }
            }
            if (n > 0) table.withPool(pool);
        });
    }
}
