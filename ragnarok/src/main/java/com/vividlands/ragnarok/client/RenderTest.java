package com.vividlands.ragnarok.client;

import com.vividlands.ragnarok.Ragnarok;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.Difficulty;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.WorldDataConfiguration;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;

import java.util.ArrayList;
import java.util.List;

/**
 * Automatic render test (CI only, -Dvividlands.rendertest=true): creates a creative world, builds a platform in the
 * sky, dresses four armour stands in the Viking sets, takes screenshots from several angles and closes the game.
 */
final class RenderTest {
    private static final String[] SETS = {"berserker", "ulfhednar", "valkyrie", "jarl"};
    private static final String[] WEAPONS = {"bearded_axe", "wolf_seax", "valkyrie_sword", "dane_axe", "gungnir",
            "fenrirs_fang", "round_shield", "khopesh", "guandao", "gladius", "kopis", "macuahuitl", "katana", "zweihander",
            "ragnarok"};
    private static int tick;
    private static int stage;
    private static int wait;
    private static final List<Runnable> steps = new ArrayList<>();

    private RenderTest() {
    }

    static void install() {
        ClientTickEvents.END_CLIENT_TICK.register(RenderTest::onTick);
    }

    private static void cmd(Minecraft mc, String command) {
        MinecraftServer server = mc.getSingleplayerServer();
        if (server == null) return;
        server.execute(() -> server.getCommands().performPrefixedCommand(server.createCommandSourceStack(), command));
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, name + ".png", mc.getMainRenderTarget(),
                msg -> Ragnarok.LOG.info("render test screenshot: {}", msg.getString()));
    }

    private static String stand(String set, double x, double z, float yaw) {
        String p = "vividlands_ragnarok:" + set + "_";
        return String.format(java.util.Locale.ROOT,
                "summon minecraft:armor_stand %.1f 200 %.1f {ShowArms:1b,NoBasePlate:1b,NoGravity:1b,Rotation:[%.0ff,0f],"
                        + "Pose:{RightArm:[-10f,0f,10f],LeftArm:[-10f,0f,-10f]},ArmorItems:[{id:\"%sboots\",Count:1b},"
                        + "{id:\"%sleggings\",Count:1b},{id:\"%schestplate\",Count:1b},{id:\"%shelmet\",Count:1b}]}",
                x, z, yaw, p, p, p, p);
    }

    private static void plan(Minecraft mc) {
        steps.add(() -> {
            for (String c : new String[]{"gamerule doDaylightCycle false", "time set 6000", "weather clear",
                    "gamerule doMobSpawning false", "tp @a 0.5 202 8.5 180 0"}) cmd(mc, c);
        });
        steps.add(() -> {
            cmd(mc, "fill -10 199 -8 12 199 8 minecraft:smooth_stone");
            cmd(mc, "fill -10 200 -8 12 206 8 minecraft:air");
            for (int i = 0; i < SETS.length; i++) cmd(mc, stand(SETS[i], -4.5 + i * 3, 0.5, 0));
            mc.options.hideGui = true;
        });
        // the whole line-up from the front, the back and an angle
        steps.add(() -> cmd(mc, "tp @a 0.5 201.2 7.5 180 6"));
        steps.add(() -> shot(mc, "lineup_front"));
        steps.add(() -> cmd(mc, "tp @a 0.5 201.2 -6.5 0 6"));
        steps.add(() -> shot(mc, "lineup_back"));
        steps.add(() -> cmd(mc, "tp @a 8.5 202.2 6.0 125 14"));
        steps.add(() -> shot(mc, "lineup_angle"));
        // close-ups of every set, front and back
        for (int i = 0; i < SETS.length; i++) {
            double x = -4.5 + i * 3;
            String set = SETS[i];
            steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a %.1f 201.1 3.1 180 4", x)));
            steps.add(() -> shot(mc, set + "_front"));
            steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a %.1f 201.1 -2.1 0 4", x)));
            steps.add(() -> shot(mc, set + "_back"));
            steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a %.1f 201.5 2.6 145 12", x + 1.9)));
            steps.add(() -> shot(mc, set + "_angle"));
        }
        // hand rotation check: a vanilla iron sword next to three candidate rotations of one weapon
        steps.add(() -> {
            mc.options.hideGui = true;
            cmd(mc, "fill -8 199 12 10 199 24 minecraft:smooth_stone");
            String[] items = {"minecraft:iron_sword", "vividlands_ragnarok:test_view_a", "vividlands_ragnarok:test_view_b",
                    "vividlands_ragnarok:test_view_c"};
            for (int i = 0; i < items.length; i++) {
                cmd(mc, String.format(java.util.Locale.ROOT,
                        "summon minecraft:armor_stand %.1f 200 19.5 {ShowArms:1b,NoBasePlate:1b,NoGravity:1b,Rotation:[180f,0f],"
                                + "Pose:{RightArm:[-20f,0f,0f]},HandItems:[{id:\"%s\",Count:1b},{}]}", -3.5 + i * 3, items[i]));
            }
        });
        steps.add(() -> cmd(mc, "tp @a 1.0 201.0 15.5 0 8"));
        steps.add(() -> shot(mc, "rotation_check_front"));
        steps.add(() -> cmd(mc, "tp @a 9.0 201.0 19.5 90 6"));
        steps.add(() -> shot(mc, "rotation_check_side"));
        steps.add(() -> { if (mc.player != null) { mc.player.getAbilities().flying = true; mc.player.onUpdateAbilities(); } });
        steps.add(() -> cmd(mc, "tp @a 1.0 206.0 19.5 0 90"));
        steps.add(() -> shot(mc, "rotation_check_top"));
        for (int i = 0; i < 4; i++) {
            double x = -3.5 + i * 3;
            int k = i;
            steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a %.1f 201.0 17.0 0 8", x)));
            steps.add(() -> shot(mc, "rotation_check_close_" + k));
        }
        // weapons: a row of armour stands holding them, facing the camera
        steps.add(() -> {
            mc.options.hideGui = true;
            cmd(mc, "fill -14 199 6 14 199 14 minecraft:smooth_stone");
            cmd(mc, "fill -14 200 6 14 206 14 minecraft:air");
            for (int i = 0; i < WEAPONS.length; i++) {
                cmd(mc, String.format(java.util.Locale.ROOT,
                        "summon minecraft:armor_stand %.1f 200 11.5 {ShowArms:1b,NoBasePlate:1b,NoGravity:1b,Rotation:[180f,0f],"
                                + "Pose:{RightArm:[-20f,0f,0f]},HandItems:[{id:\"vividlands_ragnarok:%s\",Count:1b},{}]}",
                        -10.5 + i * 1.5, WEAPONS[i]));
            }
        });
        steps.add(() -> cmd(mc, "tp @a 0.5 201.6 5.0 0 8"));
        steps.add(() -> shot(mc, "weapons_row"));
        steps.add(() -> cmd(mc, "tp @a -6.0 201.3 8.5 0 6"));
        steps.add(() -> shot(mc, "weapons_left"));
        steps.add(() -> cmd(mc, "tp @a 6.0 201.3 8.5 0 6"));
        steps.add(() -> shot(mc, "weapons_right"));
        // first person with the hotbar full of weapons
        steps.add(() -> {
            for (int i = 0; i < 9; i++) {
                cmd(mc, "item replace entity @a hotbar." + i + " with vividlands_ragnarok:" + WEAPONS[i]);
            }
            cmd(mc, "item replace entity @a weapon.offhand with vividlands_ragnarok:round_shield");
            cmd(mc, "tp @a 0.5 201 -20 0 0");
            mc.options.hideGui = false;
        });
        for (int slot : new int[]{0, 3, 4, 5}) {
            steps.add(() -> { if (mc.player != null) mc.player.getInventory().selected = slot; });
            steps.add(() -> shot(mc, "firstperson_" + WEAPONS[slot]));
        }
        steps.add(() -> {
            for (int i = 0; i < 6; i++) {
                cmd(mc, "item replace entity @a hotbar." + i + " with vividlands_ragnarok:" + WEAPONS[9 + i]);
            }
            if (mc.player != null) mc.player.getInventory().selected = 5;
        });
        steps.add(() -> shot(mc, "firstperson_ragnarok"));
        String[] fp = {"minecraft:iron_sword", "vividlands_ragnarok:test_view_a", "vividlands_ragnarok:test_view_b",
                "vividlands_ragnarok:test_view_c"};
        for (String it : fp) {
            steps.add(() -> {
                cmd(mc, "item replace entity @a hotbar.0 with " + it);
                if (mc.player != null) mc.player.getInventory().selected = 0;
            });
            steps.add(() -> shot(mc, "firstperson_check_" + it.substring(it.indexOf(':') + 1)));
        }
        steps.add(mc::stop);
    }

    private static void onTick(Minecraft mc) {
        tick++;
        if (stage == 0) {
            // first launch shows the accessibility welcome screen instead of the title screen: just wait for
            // resources to finish loading, then create the world from whatever screen is open
            if (tick > 60 && mc.getOverlay() == null && mc.level == null) {
                stage = 1;
                Ragnarok.LOG.info("render test: creating world");
                mc.createWorldOpenFlows().createFreshLevel("rendertest",
                        new LevelSettings("rendertest", GameType.CREATIVE, false, Difficulty.PEACEFUL, true,
                                new GameRules(), WorldDataConfiguration.DEFAULT),
                        new WorldOptions(20261018L, false, false), WorldPresets::createNormalWorldDimensions);
            }
            return;
        }
        if (stage == 1) {
            if (mc.player != null && mc.level != null) {
                stage = 2;
                wait = 100;
                plan(mc);
                Ragnarok.LOG.info("render test: in world, {} steps", steps.size());
            }
            return;
        }
        if (--wait > 0 || steps.isEmpty()) return;
        steps.remove(0).run();
        wait = 50;                      // let chunks load and the camera settle between steps
    }
}
