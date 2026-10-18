package com.vividlands.ragnarok.armor;

import com.vividlands.ragnarok.Ragnarok;
import com.vividlands.ragnarok.generator.Generators;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.block.Block;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/**
 * Viking endgame armor (four sets) and the boss trophies they are made from.
 * Full-set bonuses are applied once a second:
 *   Berserker  - Strength I below half health, Strength II below a quarter (rage)
 *   Ulfhednar  - Speed I, Night Vision at night (the wolf's senses)
 *   Valkyrie   - Jump Boost I, Slow Falling while falling (unless sneaking)
 *   Jarl       - Resistance I and Fire Resistance
 */
public final class VikingArmor {
    public static final Map<VikingArmorMaterial, Map<ArmorItem.Type, VikingArmorItem>> PIECES = new EnumMap<>(VikingArmorMaterial.class);
    public static final List<Item> TROPHIES = new ArrayList<>();
    private static final String[][] TROPHY_IDS = {
            {"bear_pelt", "uncommon"}, {"saber_fang", "uncommon"}, {"wolf_pelt", "rare"}, {"eclipse_shard", "rare"},
            {"raven_feather", "rare"}, {"sleipnir_hair", "rare"}, {"dragon_gold", "epic"}, {"serpent_scale", "epic"}};
    private static final String[] PIECE_NAMES = {"helmet", "chestplate", "leggings", "boots"};

    private VikingArmor() {
    }

    public static void register() {
        for (String[] t : TROPHY_IDS) {
            Rarity r = switch (t[1]) {
                case "epic" -> Rarity.EPIC;
                case "rare" -> Rarity.RARE;
                default -> Rarity.UNCOMMON;
            };
            TROPHIES.add(Registry.register(BuiltInRegistries.ITEM, new ResourceLocation(Ragnarok.MOD_ID, t[0]),
                    new Item(new Item.Properties().rarity(r))));
        }
        ArmorItem.Type[] types = {ArmorItem.Type.HELMET, ArmorItem.Type.CHESTPLATE, ArmorItem.Type.LEGGINGS, ArmorItem.Type.BOOTS};
        for (VikingArmorMaterial set : VikingArmorMaterial.values()) {
            Map<ArmorItem.Type, VikingArmorItem> pieces = new EnumMap<>(ArmorItem.Type.class);
            Rarity rarity = set == VikingArmorMaterial.JARL ? Rarity.EPIC : (set == VikingArmorMaterial.BERSERKER ? Rarity.UNCOMMON : Rarity.RARE);
            for (int i = 0; i < 4; i++) {
                VikingArmorItem item = new VikingArmorItem(set, types[i], new Item.Properties().rarity(rarity)
                        .fireResistant());
                pieces.put(types[i], Registry.register(BuiltInRegistries.ITEM,
                        new ResourceLocation(Ragnarok.MOD_ID, set.id() + "_" + PIECE_NAMES[i]), item));
            }
            PIECES.put(set, pieces);
        }
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, new ResourceLocation(Ragnarok.MOD_ID, "main"),
                FabricItemGroup.builder()
                        .title(Component.translatable("itemGroup.vividlands_ragnarok"))
                        .icon(() -> new ItemStack(PIECES.get(VikingArmorMaterial.JARL).get(ArmorItem.Type.HELMET)))
                        .displayItems((params, out) -> {
                            for (Map<ArmorItem.Type, VikingArmorItem> set : PIECES.values()) {
                                set.values().forEach(out::accept);
                            }
                            com.vividlands.ragnarok.weapon.Weapons.ITEMS.forEach(out::accept);
                            TROPHIES.forEach(out::accept);
                            for (Block b : Generators.BLOCKS) out.accept(b);
                        })
                        .build());
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (server.getTickCount() % 20 != 0) return;
            for (ServerPlayer player : server.getPlayerList().getPlayers()) {
                applySetBonus(player);
            }
        });
    }

    /** The set the player wears in full, or null. */
    public static VikingArmorMaterial fullSet(ServerPlayer player) {
        VikingArmorMaterial set = null;
        for (EquipmentSlot slot : new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) {
            if (!(player.getItemBySlot(slot).getItem() instanceof VikingArmorItem piece)) return null;
            if (set == null) set = piece.set();
            else if (set != piece.set()) return null;
        }
        return set;
    }

    private static void give(ServerPlayer p, MobEffect effect, int amplifier, int duration) {
        p.addEffect(new MobEffectInstance(effect, duration, amplifier, true, false, true));
    }

    private static void applySetBonus(ServerPlayer p) {
        VikingArmorMaterial set = fullSet(p);
        if (set == null) return;
        switch (set) {
            case BERSERKER -> {
                float frac = p.getHealth() / p.getMaxHealth();
                if (frac <= 0.25f) give(p, MobEffects.DAMAGE_BOOST, 1, 40);
                else if (frac <= 0.5f) give(p, MobEffects.DAMAGE_BOOST, 0, 40);
            }
            case ULFHEDNAR -> {
                give(p, MobEffects.MOVEMENT_SPEED, 0, 40);
                if (p.level().isNight()) give(p, MobEffects.NIGHT_VISION, 0, 300);
            }
            case VALKYRIE -> {
                give(p, MobEffects.JUMP, 0, 40);
                if (p.fallDistance > 2.5f && !p.isShiftKeyDown()) give(p, MobEffects.SLOW_FALLING, 0, 30);
            }
            case JARL -> {
                give(p, MobEffects.DAMAGE_RESISTANCE, 0, 40);
                give(p, MobEffects.FIRE_RESISTANCE, 0, 40);
            }
        }
    }
}
