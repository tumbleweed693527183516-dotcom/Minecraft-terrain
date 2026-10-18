package com.vividlands.ragnarok.weapon;

import com.vividlands.ragnarok.Ragnarok;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Supplier;

/**
 * The pack's weapons, each drawn with its 3D GeckoLib model (geo/item/weapon/<id>.geo.json).
 * Stats are placeholders for now (to be balanced later); swing animations come from Better Combat
 * (data/vividlands_ragnarok/weapon_attributes).
 */
public final class Weapons {
    public static final List<Item> ITEMS = new ArrayList<>();

    /** Placeholder material for every weapon: durability and enchantability only (damage is per weapon). */
    enum WeaponTier implements Tier {
        VIKING(1800, 15), LEGENDARY(3000, 20);

        private final int uses;
        private final int enchant;

        WeaponTier(int uses, int enchant) {
            this.uses = uses;
            this.enchant = enchant;
        }

        @Override public int getUses() { return uses; }
        @Override public float getSpeed() { return 8.0f; }
        @Override public float getAttackDamageBonus() { return 0.0f; }
        @Override public int getLevel() { return 4; }
        @Override public int getEnchantmentValue() { return enchant; }
        @Override public Ingredient getRepairIngredient() { return Ingredient.EMPTY; }
    }

    private Weapons() {
    }

    private static void lore(String id, List<Component> tooltip) {
        tooltip.add(Component.translatable("tooltip.vividlands_ragnarok.weapon." + id).withStyle(ChatFormatting.GOLD));
    }

    // ---- the three item kinds: sword-like, axe, shield (all GeckoLib items) ----
    public static class GeoSword extends SwordItem implements GeoItem {
        private final String id;
        private final boolean glow;
        private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
        private final Supplier<Object> renderProvider = GeoItem.makeRenderer(this);

        GeoSword(String id, Tier tier, int damage, float speed, boolean glow, Properties p) {
            super(tier, damage, speed, p);
            this.id = id;
            this.glow = glow;
        }

        @Override public void createRenderer(Consumer<Object> c) { c.accept(WeaponRender.provider(id, glow)); }
        @Override public Supplier<Object> getRenderProvider() { return renderProvider; }
        @Override public void registerControllers(AnimatableManager.ControllerRegistrar c) { }
        @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
        @Override public void appendHoverText(ItemStack s, @Nullable Level l, List<Component> t, TooltipFlag f) { lore(id, t); }
    }

    public static class GeoAxe extends AxeItem implements GeoItem {
        private final String id;
        private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
        private final Supplier<Object> renderProvider = GeoItem.makeRenderer(this);

        GeoAxe(String id, Tier tier, float damage, float speed, Properties p) {
            super(tier, damage, speed, p);
            this.id = id;
        }

        @Override public void createRenderer(Consumer<Object> c) { c.accept(WeaponRender.provider(id, false)); }
        @Override public Supplier<Object> getRenderProvider() { return renderProvider; }
        @Override public void registerControllers(AnimatableManager.ControllerRegistrar c) { }
        @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
        @Override public void appendHoverText(ItemStack s, @Nullable Level l, List<Component> t, TooltipFlag f) { lore(id, t); }
    }

    public static class GeoShield extends ShieldItem implements GeoItem {
        private final String id;
        private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
        private final Supplier<Object> renderProvider = GeoItem.makeRenderer(this);

        GeoShield(String id, Properties p) {
            super(p);
            this.id = id;
        }

        @Override public void createRenderer(Consumer<Object> c) { c.accept(WeaponRender.provider(id, false)); }
        @Override public Supplier<Object> getRenderProvider() { return renderProvider; }
        @Override public void registerControllers(AnimatableManager.ControllerRegistrar c) { }
        @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
        @Override public void appendHoverText(ItemStack s, @Nullable Level l, List<Component> t, TooltipFlag f) { lore(id, t); }
        @Override public String getDescriptionId() { return "item.vividlands_ragnarok." + id; }
    }

    private static Item reg(String id, Item item) {
        Item it = Registry.register(BuiltInRegistries.ITEM, new ResourceLocation(Ragnarok.MOD_ID, id), item);
        ITEMS.add(it);
        return it;
    }

    private static Item.Properties props(Rarity r) {
        return new Item.Properties().rarity(r).fireResistant();
    }

    public static void register() {
        WeaponTier v = WeaponTier.VIKING, l = WeaponTier.LEGENDARY;
        // id, damage, attack speed (placeholder stats - balanced later)
        reg("bearded_axe", new GeoAxe("bearded_axe", v, 8.0f, -3.0f, props(Rarity.UNCOMMON)));
        reg("wolf_seax", new GeoSword("wolf_seax", v, 5, -2.0f, false, props(Rarity.RARE)));
        reg("valkyrie_sword", new GeoSword("valkyrie_sword", v, 7, -2.4f, false, props(Rarity.RARE)));
        reg("dane_axe", new GeoAxe("dane_axe", v, 11.0f, -3.2f, props(Rarity.EPIC)));
        reg("gungnir", new GeoSword("gungnir", l, 9, -2.8f, false, props(Rarity.EPIC)));
        reg("fenrirs_fang", new GeoSword("fenrirs_fang", l, 11, -2.6f, false, props(Rarity.EPIC)));
        reg("round_shield", new GeoShield("round_shield", new Item.Properties().durability(672).rarity(Rarity.UNCOMMON)));
        reg("khopesh", new GeoSword("khopesh", v, 6, -2.3f, false, props(Rarity.RARE)));
        reg("guandao", new GeoSword("guandao", v, 8, -2.9f, false, props(Rarity.RARE)));
        reg("gladius", new GeoSword("gladius", v, 6, -2.1f, false, props(Rarity.RARE)));
        reg("kopis", new GeoSword("kopis", v, 7, -2.5f, false, props(Rarity.RARE)));
        reg("macuahuitl", new GeoSword("macuahuitl", v, 8, -2.8f, false, props(Rarity.RARE)));
        reg("katana", new GeoSword("katana", v, 7, -2.2f, false, props(Rarity.RARE)));
        reg("zweihander", new GeoSword("zweihander", v, 10, -3.0f, false, props(Rarity.RARE)));
        reg("ragnarok", new GeoSword("ragnarok", l, 14, -2.6f, true, props(Rarity.EPIC)));
    }
}
