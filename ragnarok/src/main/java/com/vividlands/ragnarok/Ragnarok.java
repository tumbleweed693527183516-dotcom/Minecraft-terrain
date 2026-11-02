package com.vividlands.ragnarok;

import net.fabricmc.api.ModInitializer;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.Level;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Vivid Lands: Ragnarok, the modpack's own mod.
 *
 * Pack rules (mixins in com.vividlands.ragnarok.mixin):
 *  - no Warden: sculk shriekers never summon one (they still shriek and give Darkness)
 *  - the Nether is closed: obsidian frames never light, nothing travels there
 *  - the End is closed: eyes of ender can't be placed in portal frames, nothing travels there
 *  - both open for the whole world once Fenrir is killed (the epilogue, "Twilight Broken")
 * Everything those dimensions give is made with Create instead (data/vividlands_ragnarok/recipes).
 */
public class Ragnarok implements ModInitializer {
    public static final String MOD_ID = "vividlands_ragnarok";
    public static final Logger LOG = LoggerFactory.getLogger(MOD_ID);

    /** The Nether and the End stay sealed until someone kills Fenrir (no server known: sealed). */
    public static boolean closed(ResourceKey<Level> dimension, net.minecraft.server.MinecraftServer server) {
        if (dimension != Level.NETHER && dimension != Level.END) return false;
        return server == null || !com.vividlands.ragnarok.boss.BossProgress.get(server).realmsOpen();
    }

    /** Whether the realms are still sealed in this level's world. */
    public static boolean sealed(net.minecraft.world.level.LevelAccessor level) {
        return closed(Level.NETHER, level.getServer());
    }

    @Override
    public void onInitialize() {
        // Load every class the pack rules patch now, so a rule that fails to apply stops the game at
        // startup (with a clear mixin error) instead of silently letting the Warden or a portal through.
        Class<?>[] patched = {net.minecraft.world.level.block.entity.SculkShriekerBlockEntity.class,
                net.minecraft.world.level.portal.PortalShape.class, net.minecraft.world.item.EnderEyeItem.class,
                net.minecraft.world.entity.Entity.class, net.minecraft.server.level.ServerPlayer.class};
        com.vividlands.ragnarok.generator.Generators.register();
        com.vividlands.ragnarok.weapon.Weapons.register();
        com.vividlands.ragnarok.armor.VikingArmor.register();
        com.vividlands.ragnarok.armor.AncientArmor.register();
        com.vividlands.ragnarok.armor.Glamour.register();
        com.vividlands.ragnarok.armor.ArmorTraits.register();
        com.vividlands.ragnarok.classes.Classes.register();
        com.vividlands.ragnarok.quest.QuestHooks.register();
        com.vividlands.ragnarok.boss.Bosses.register();
        com.vividlands.ragnarok.loot.ClosedRealmLoot.register();
        LOG.info("Vivid Lands: Ragnarok - Warden disabled, Nether and End closed ({} rules); cobblestone generators MK1-MK5",
                patched.length);
    }
}
