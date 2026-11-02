package com.vividlands.ragnarok.armor;

import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterials;
import net.minecraft.world.item.ItemStack;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * What armor does beyond its armor bars.
 *
 * <p><b>Boss Ward.</b> Every boss belongs to a stage of the story (Chapter 1 acts I-IV, then the five Chapter 2
 * bosses), and every full armor set has a ward: the stage it was made for. A boss's hits are multiplied by how far
 * the wearer's ward is behind that stage: ward caught up = half damage, one stage behind = 0.85, two = 1.2, three or
 * more = 1.5. So the armor from the act before a boss makes the fight fair, and skipping it makes it hard. Vanilla
 * sets count too: full iron = ward 1, diamond = 2, netherite = 3.
 *
 * <p><b>Set bonus.</b> A full ancient set also gives its civilization family's trait.
 */
public final class ArmorTraits {
    private ArmorTraits() {
    }

    // ------------------------------------------------------------------ boss ward
    /** The story stage of each boss: Chapter 1 acts 1-4, Chapter 2 bosses 5-9. */
    public static final Map<String, Integer> BOSS_STAGE = Map.ofEntries(
            Map.entry("cave_bear", 1), Map.entry("dire_wolf", 1), Map.entry("irish_elk", 1), Map.entry("terror_bird", 1),
            Map.entry("steppe_bison", 1),
            Map.entry("hippo", 2), Map.entry("komodo", 2), Map.entry("crocodile", 2), Map.entry("cave_lion", 2),
            Map.entry("saber_tooth", 2),
            Map.entry("haast_eagle", 3), Map.entry("anaconda", 3), Map.entry("silverback", 3), Map.entry("glyptodon", 3),
            Map.entry("walrus", 3),
            Map.entry("ground_sloth", 4), Map.entry("bull_shark", 4), Map.entry("woolly_rhino", 4), Map.entry("elephant", 4),
            Map.entry("mammoth", 4),
            Map.entry("sleipnir", 5), Map.entry("garmr", 6), Map.entry("fafnir", 7), Map.entry("jormungandr", 8),
            Map.entry("fenrir", 9));

    /** Stage names for tooltips, by ward. */
    private static final String[] STAGE_NAMES = {"none", "Act I", "Act II", "Act III", "Act IV", "Sleipnir", "Garmr",
            "Fafnir", "Jormungandr", "Fenrir"};

    /** The ward an ancient set gives, from its tier (the quest book hands out tiers in these bands). */
    public static int wardOfTier(int tier) {
        if (tier <= 5) return 1;
        if (tier <= 15) return 2;
        if (tier <= 25) return 3;
        if (tier <= 35) return 4;
        if (tier <= 40) return 5;
        if (tier <= 42) return 6;
        if (tier <= 44) return 7;
        if (tier <= 46) return 8;
        return 9;
    }

    public static String stageName(int ward) {
        return STAGE_NAMES[Math.max(0, Math.min(STAGE_NAMES.length - 1, ward))];
    }

    /** The ward of the full set the entity wears, or 0. */
    public static int ward(LivingEntity e) {
        AncientArmorMaterial set = fullAncientSet(e);
        if (set != null) return wardOfTier(set.tier());
        Object material = null;
        for (EquipmentSlot slot : ARMOR) {
            ItemStack s = e.getItemBySlot(slot);
            if (!(s.getItem() instanceof ArmorItem a)) return 0;
            if (material == null) material = a.getMaterial();
            else if (material != a.getMaterial()) return 0;
        }
        if (material instanceof VikingArmorMaterial v) return switch (v) {     // the Viking sets come from boss trophies
            case BERSERKER -> 2;
            case ULFHEDNAR -> 3;
            case VALKYRIE -> 5;
            case JARL -> 9;
        };
        if (material == ArmorMaterials.IRON) return 1;
        if (material == ArmorMaterials.DIAMOND) return 2;
        if (material == ArmorMaterials.NETHERITE) return 3;
        return 0;
    }

    /** Damage multiplier for a boss hit on this entity. */
    public static float wardMultiplier(LivingEntity target, String bossId) {
        Integer stage = BOSS_STAGE.get(bossId);
        if (stage == null) return 1f;
        int gap = stage - ward(target);
        return gap <= 0 ? 0.5f : gap == 1 ? 0.85f : gap == 2 ? 1.2f : 1.5f;
    }

    private static final EquipmentSlot[] ARMOR = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};

    /** The ancient set worn in all four slots, or null. */
    public static AncientArmorMaterial fullAncientSet(LivingEntity e) {
        AncientArmorMaterial m = null;
        for (EquipmentSlot slot : ARMOR) {
            if (!(e.getItemBySlot(slot).getItem() instanceof AncientArmorItem a)) return null;
            if (m == null) m = a.ancientMaterial();
            else if (m != a.ancientMaterial()) return null;
        }
        return m;
    }

    // ------------------------------------------------------------------ set bonuses
    public enum Trait {
        BUILDER("Builder", "Haste I: the people who raised the ziggurats"),
        SUN("Sun-Hardened", "Fire resistance: born under a desert sun"),
        SEAFARER("Seafarer", "Water breathing and faster swimming"),
        PHALANX("Phalanx", "+40% knockback resistance and +2 armor: hold the line"),
        HORSE_LORD("Horse Lord", "+15% movement speed: the steppe is wide"),
        FURY("Fury", "+2 attack damage: the charge of the war-bands"),
        LEGION("Legion", "Regeneration I while below half health"),
        DISCIPLINE("Discipline", "+15% attack speed: a thousand drills"),
        JUNGLE("Jungle-Born", "Immune to poison and hunger"),
        KING_OF_MEN("King of Men", "Phalanx, plus Strength I and Resistance I");

        public final String title, text;

        Trait(String title, String text) {
            this.title = title;
            this.text = text;
        }
    }

    public static final Map<String, Trait> TRAITS = Map.ofEntries(
            Map.entry("sumerian", Trait.BUILDER), Map.entry("akkadian", Trait.BUILDER), Map.entry("assyrian", Trait.BUILDER),
            Map.entry("babylonian", Trait.BUILDER), Map.entry("persian", Trait.BUILDER), Map.entry("hittite", Trait.BUILDER),
            Map.entry("egyptian", Trait.SUN), Map.entry("nubian", Trait.SUN), Map.entry("aksumite", Trait.SUN),
            Map.entry("numidian", Trait.SUN), Map.entry("pharaoh", Trait.SUN),
            Map.entry("minoan", Trait.SEAFARER), Map.entry("phoenician", Trait.SEAFARER), Map.entry("carthaginian", Trait.SEAFARER),
            Map.entry("athenian", Trait.SEAFARER),
            Map.entry("mycenaean", Trait.PHALANX), Map.entry("spartan", Trait.PHALANX), Map.entry("macedonian", Trait.PHALANX),
            Map.entry("argyraspid", Trait.PHALANX), Map.entry("byzantine", Trait.PHALANX),
            Map.entry("scythian", Trait.HORSE_LORD), Map.entry("sarmatian", Trait.HORSE_LORD), Map.entry("parthian", Trait.HORSE_LORD),
            Map.entry("hun", Trait.HORSE_LORD), Map.entry("mongol", Trait.HORSE_LORD),
            Map.entry("celtic", Trait.FURY), Map.entry("germanic", Trait.FURY), Map.entry("dacian", Trait.FURY),
            Map.entry("thracian", Trait.FURY), Map.entry("illyrian", Trait.FURY), Map.entry("iberian", Trait.FURY),
            Map.entry("anglo_saxon", Trait.FURY),
            Map.entry("roman", Trait.LEGION), Map.entry("centurion", Trait.LEGION), Map.entry("praetorian", Trait.LEGION),
            Map.entry("gladiator", Trait.LEGION), Map.entry("etruscan", Trait.LEGION),
            Map.entry("shang", Trait.DISCIPLINE), Map.entry("qin", Trait.DISCIPLINE), Map.entry("han", Trait.DISCIPLINE),
            Map.entry("goguryeo", Trait.DISCIPLINE), Map.entry("samurai", Trait.DISCIPLINE),
            Map.entry("olmec", Trait.JUNGLE), Map.entry("maya", Trait.JUNGLE), Map.entry("aztec", Trait.JUNGLE),
            Map.entry("inca", Trait.JUNGLE), Map.entry("khmer", Trait.JUNGLE), Map.entry("maurya", Trait.JUNGLE),
            Map.entry("agamemnon", Trait.KING_OF_MEN));

    public static Trait traitOf(String setId) {
        return TRAITS.getOrDefault(setId, Trait.PHALANX);
    }

    private static final UUID KNOCKBACK = UUID.fromString("6c0e6f21-6b8e-4f7a-9d3b-1f6a2c7e9a01");
    private static final UUID ARMOR_BONUS = UUID.fromString("6c0e6f21-6b8e-4f7a-9d3b-1f6a2c7e9a02");
    private static final UUID SPEED = UUID.fromString("6c0e6f21-6b8e-4f7a-9d3b-1f6a2c7e9a03");
    private static final UUID DAMAGE = UUID.fromString("6c0e6f21-6b8e-4f7a-9d3b-1f6a2c7e9a04");
    private static final UUID ATTACK_SPEED = UUID.fromString("6c0e6f21-6b8e-4f7a-9d3b-1f6a2c7e9a05");

    private record Mod(Attribute attribute, UUID id, double amount, AttributeModifier.Operation op) {
    }

    private static List<Mod> mods(Trait t) {
        if (t == null) return List.of();
        return switch (t) {
            case PHALANX, KING_OF_MEN -> List.of(new Mod(Attributes.KNOCKBACK_RESISTANCE, KNOCKBACK, 0.4, AttributeModifier.Operation.ADDITION),
                    new Mod(Attributes.ARMOR, ARMOR_BONUS, 2, AttributeModifier.Operation.ADDITION));
            case HORSE_LORD -> List.of(new Mod(Attributes.MOVEMENT_SPEED, SPEED, 0.15, AttributeModifier.Operation.MULTIPLY_BASE));
            case FURY -> List.of(new Mod(Attributes.ATTACK_DAMAGE, DAMAGE, 2, AttributeModifier.Operation.ADDITION));
            case DISCIPLINE -> List.of(new Mod(Attributes.ATTACK_SPEED, ATTACK_SPEED, 0.15, AttributeModifier.Operation.MULTIPLY_BASE));
            default -> List.of();
        };
    }

    private static final Mod[] ALL = {
            new Mod(Attributes.KNOCKBACK_RESISTANCE, KNOCKBACK, 0, AttributeModifier.Operation.ADDITION),
            new Mod(Attributes.ARMOR, ARMOR_BONUS, 0, AttributeModifier.Operation.ADDITION),
            new Mod(Attributes.MOVEMENT_SPEED, SPEED, 0, AttributeModifier.Operation.MULTIPLY_BASE),
            new Mod(Attributes.ATTACK_DAMAGE, DAMAGE, 0, AttributeModifier.Operation.ADDITION),
            new Mod(Attributes.ATTACK_SPEED, ATTACK_SPEED, 0, AttributeModifier.Operation.MULTIPLY_BASE)};

    private static void effect(ServerPlayer p, MobEffect e, int amp) {
        p.addEffect(new MobEffectInstance(e, 60, amp, true, false, true));
    }

    private static void tick(ServerPlayer p) {
        AncientArmorMaterial set = fullAncientSet(p);
        Trait t = set == null ? null : traitOf(set.set().id());
        // attribute bonuses: add the trait's, remove every other
        List<Mod> want = mods(t);
        for (Mod m : ALL) {
            AttributeInstance inst = p.getAttribute(m.attribute());
            if (inst == null) continue;
            Mod w = want.stream().filter(x -> x.id().equals(m.id())).findFirst().orElse(null);
            AttributeModifier cur = inst.getModifier(m.id());
            if (w == null) {
                if (cur != null) inst.removeModifier(m.id());
            } else if (cur == null) {
                inst.addTransientModifier(new AttributeModifier(w.id(), "Ancient set bonus", w.amount(), w.op()));
            }
        }
        if (t == null) return;
        com.vividlands.ragnarok.quest.QuestHooks.award(p, "armor/full_set");
        switch (t) {
            case BUILDER -> effect(p, MobEffects.DIG_SPEED, 0);
            case SUN -> effect(p, MobEffects.FIRE_RESISTANCE, 0);
            case SEAFARER -> {
                effect(p, MobEffects.WATER_BREATHING, 0);
                if (p.isInWater()) effect(p, MobEffects.DOLPHINS_GRACE, 0);
            }
            case LEGION -> {
                if (p.getHealth() < p.getMaxHealth() / 2) effect(p, MobEffects.REGENERATION, 0);
            }
            case JUNGLE -> {
                p.removeEffect(MobEffects.POISON);
                p.removeEffect(MobEffects.HUNGER);
            }
            case KING_OF_MEN -> {
                effect(p, MobEffects.DAMAGE_BOOST, 0);
                effect(p, MobEffects.DAMAGE_RESISTANCE, 0);
            }
            default -> {
            }
        }
    }

    public static void register() {
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (server.getTickCount() % 20 != 0) return;
            for (ServerPlayer p : server.getPlayerList().getPlayers()) tick(p);
        });
    }

    // ------------------------------------------------------------------ tooltip lines
    /** The local player, set by the client, so tooltips can count how much of a set you wear. */
    public static java.util.function.Supplier<LivingEntity> clientWearer = () -> null;

    public static void tooltip(AncientArmorMaterial m, List<Component> lines) {
        Trait t = traitOf(m.set().id());
        int ward = wardOfTier(m.tier());
        lines.add(Component.literal("Boss Ward: ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal(stageName(ward)).withStyle(ChatFormatting.GREEN)));
        int worn = 0;
        LivingEntity e = clientWearer.get();
        if (e != null) {
            for (EquipmentSlot slot : ARMOR) {
                if (e.getItemBySlot(slot).getItem() instanceof AncientArmorItem a && a.ancientMaterial() == m) worn++;
            }
        }
        lines.add(Component.literal(t.title).withStyle(worn == 4 ? ChatFormatting.AQUA : ChatFormatting.DARK_AQUA)
                .append(Component.literal("  set " + worn + "/4").withStyle(ChatFormatting.DARK_GRAY)));
        lines.add(Component.literal(t.text).withStyle(ChatFormatting.GRAY));
    }

}
