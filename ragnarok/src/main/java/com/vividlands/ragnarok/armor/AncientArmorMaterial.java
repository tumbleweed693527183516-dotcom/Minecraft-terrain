package com.vividlands.ragnarok.armor;

import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.crafting.Ingredient;

/**
 * One ancient armor set's material. Every stat is a straight line from the weakest set (tier 1, about leather) to the
 * strongest (the last tier, above netherite): 11 to 24 armor, 0 to 6 toughness, so each set is a small, even step up.
 * What a set is really for is its Boss Ward and set bonus (ArmorTraits).
 */
public final class AncientArmorMaterial implements ArmorMaterial {
    // per slot: helmet, chestplate, leggings, boots
    private static final double[] DEF_MIN = {2, 4, 3, 2}, DEF_MAX = {4, 9, 7, 4};
    private static final int[] BASE_DURABILITY = {11, 16, 15, 13};

    private final AncientSets.Set set;
    private final int tier, tiers;

    AncientArmorMaterial(AncientSets.Set set, int tier, int tiers) {
        this.set = set;
        this.tier = tier;
        this.tiers = tiers;
    }

    public AncientSets.Set set() {
        return set;
    }

    public int tier() {
        return tier;
    }

    /** 0 for the first set, 1 for the last. */
    public double progress() {
        return tiers <= 1 ? 1 : (tier - 1) / (double) (tiers - 1);
    }

    private double lerp(double a, double b) {
        return a + (b - a) * progress();
    }

    private static int index(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> 0;
            case CHESTPLATE -> 1;
            case LEGGINGS -> 2;
            case BOOTS -> 3;
        };
    }

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        return BASE_DURABILITY[index(type)] * (int) Math.round(lerp(7, 45));
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        int i = index(type);
        return (int) Math.round(lerp(DEF_MIN[i], DEF_MAX[i]));
    }

    @Override
    public int getEnchantmentValue() {
        return (int) Math.round(lerp(12, 22));
    }

    @Override
    public SoundEvent getEquipSound() {
        double p = progress();
        return p < 0.25 ? SoundEvents.ARMOR_EQUIP_LEATHER : p < 0.5 ? SoundEvents.ARMOR_EQUIP_CHAIN
                : p < 0.8 ? SoundEvents.ARMOR_EQUIP_IRON : SoundEvents.ARMOR_EQUIP_NETHERITE;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return Ingredient.EMPTY;                           // repair materials come with the crafting recipes
    }

    @Override
    public String getName() {
        return "vividlands_ragnarok:" + set.id();
    }

    @Override
    public float getToughness() {
        return (float) (Math.round(lerp(0, 6) * 2) / 2.0);
    }

    @Override
    public float getKnockbackResistance() {
        return (float) (Math.round(lerp(0, 0.15) * 100) / 100.0);
    }
}
