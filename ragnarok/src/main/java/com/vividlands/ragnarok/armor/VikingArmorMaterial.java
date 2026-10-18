package com.vividlands.ragnarok.armor;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.crafting.Ingredient;

/**
 * The four Viking endgame sets, weakest to strongest. Defense per piece is helmet, chestplate, leggings, boots.
 * (Diamond is 3/8/6/3 with toughness 2; netherite 3/8/6/3 with toughness 3 and 0.1 knockback resistance.)
 */
public enum VikingArmorMaterial implements ArmorMaterial {
    BERSERKER("berserker", 30, new int[]{3, 7, 6, 3}, 1.0f, 0.0f, 15, SoundEvents.ARMOR_EQUIP_LEATHER, "bear_pelt"),
    ULFHEDNAR("ulfhednar", 35, new int[]{3, 8, 6, 3}, 2.0f, 0.05f, 15, SoundEvents.ARMOR_EQUIP_CHAIN, "wolf_pelt"),
    VALKYRIE("valkyrie", 37, new int[]{3, 8, 7, 3}, 3.0f, 0.1f, 18, SoundEvents.ARMOR_EQUIP_IRON, "raven_feather"),
    JARL("jarl", 45, new int[]{4, 9, 7, 4}, 4.0f, 0.15f, 20, SoundEvents.ARMOR_EQUIP_NETHERITE, "serpent_scale");

    private static final int[] BASE_DURABILITY = {11, 16, 15, 13};    // vanilla per-slot multipliers (helmet..boots)

    private final String name;
    private final int durabilityMultiplier;
    private final int[] defense;
    private final float toughness;
    private final float knockbackResistance;
    private final int enchantability;
    private final SoundEvent sound;
    private final String repairItem;

    VikingArmorMaterial(String name, int durabilityMultiplier, int[] defense, float toughness, float knockbackResistance,
                        int enchantability, SoundEvent sound, String repairItem) {
        this.name = name;
        this.durabilityMultiplier = durabilityMultiplier;
        this.defense = defense;
        this.toughness = toughness;
        this.knockbackResistance = knockbackResistance;
        this.enchantability = enchantability;
        this.sound = sound;
        this.repairItem = repairItem;
    }

    private static int index(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> 0;
            case CHESTPLATE -> 1;
            case LEGGINGS -> 2;
            case BOOTS -> 3;
        };
    }

    public String id() {
        return name;
    }

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        return BASE_DURABILITY[index(type)] * durabilityMultiplier;
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        return defense[index(type)];
    }

    @Override
    public int getEnchantmentValue() {
        return enchantability;
    }

    @Override
    public SoundEvent getEquipSound() {
        return sound;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return Ingredient.of(BuiltInRegistries.ITEM.get(new ResourceLocation("vividlands_ragnarok", repairItem)));
    }

    @Override
    public String getName() {
        return "vividlands_ragnarok:" + name;
    }

    @Override
    public float getToughness() {
        return toughness;
    }

    @Override
    public float getKnockbackResistance() {
        return knockbackResistance;
    }
}
