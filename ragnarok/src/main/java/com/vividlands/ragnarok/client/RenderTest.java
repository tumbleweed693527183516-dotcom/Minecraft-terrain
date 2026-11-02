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
    private static int nextWait;
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

    /** Bosses scene (-Dvividlands.rendertest.scene=bosses): every boss posed on a platform next to a player-sized stand. */
    private static void planBosses(Minecraft mc) {
        String[] ids = {"cave_bear", "irish_elk", "hippo", "crocodile", "silverback", "saber_tooth", "woolly_rhino",
                "elephant", "bull_shark", "mammoth", "dire_wolf", "steppe_bison", "terror_bird", "komodo", "glyptodon",
                "cave_lion", "anaconda", "ground_sloth", "haast_eagle", "walrus", "sleipnir", "garmr", "fafnir",
                "jormungandr", "fenrir"};
        double[] dist = {13, 15, 13, 13, 13, 11, 14, 17, 0, 19, 10, 11, 11, 12, 12, 10, 16, 12, 13, 12, 11, 12, 19, 0, 15};
        // the move shown for each boss: its signature ability (the new moves for the new bosses), then stagger
        String[] moves = {"roar", "roar", "roar", "roll", "roar", "roar", "roar", "roar", "leap", "roar", "combo", "charge",
                "combo", "breath", "spin", "leap", "grab", "grab", "swoop", "slam", "combo", "breath", "breath", "breath",
                "combo"};
        steps.add(() -> {
            for (String c : new String[]{"gamerule doDaylightCycle false", "time set 6000", "weather clear",
                    "gamerule doMobSpawning false", "gamerule vividlandsBossSpawning false", "gamemode spectator @a", "tp @a 0.5 202 8.5 180 0"}) cmd(mc, c);
            mc.options.hideGui = true;
        });
        for (int i = 0; i < ids.length; i++) {
            int x = i * 64;
            String id = ids[i];
            double d = dist[i];
            boolean sea = id.equals("bull_shark") || id.equals("jormungandr");
            int r = id.equals("jormungandr") ? 24 : 15;      // the world serpent needs a bigger pool
            steps.add(() -> {
                cmd(mc, String.format(java.util.Locale.ROOT, "fill %d 199 -28 %d 199 36 minecraft:grass_block", x - 30, x + 30));
                if (sea) {
                    cmd(mc, String.format(java.util.Locale.ROOT, "fill %d 191 %d %d 199 %d minecraft:sand", x - r - 1, -r - 1, x + r + 1, r + 1));
                    cmd(mc, String.format(java.util.Locale.ROOT, "fill %d 192 %d %d 199 %d minecraft:water", x - r, -r, x + r, r));
                }
                cmd(mc, String.format(java.util.Locale.ROOT, "tp @a %d.5 205 %.1f 180 10", x, d + 6));
            });
            steps.add(() -> {
                cmd(mc, String.format(java.util.Locale.ROOT, "ragnarok boss summon %s %d.5 %d 0.5", id, x, sea ? 197 : 200));
                cmd(mc, String.format(java.util.Locale.ROOT,
                        "summon minecraft:armor_stand %d.5 200 %.1f {NoBasePlate:1b,NoGravity:1b,ShowArms:1b,Rotation:[180f,0f]}",
                        sea ? x + r - 2 : x + 2, sea ? r - 1.5 : d * 0.45));
            });
            steps.add(() -> {
                cmd(mc, "execute as @e[tag=vividlands_ragnarok.boss." + id + "] run data merge entity @s {NoAI:1b,Rotation:[330f,0f]}");
                cmd(mc, "execute as @e[tag=vividlands_ragnarok.boss." + id + "] at @s run tp @s " + x + ".5 ~ 0.5 -30 0");
            });
            String front = id.equals("bull_shark") ? String.format(java.util.Locale.ROOT, "tp @a %d.5 204 13 180 35", x)
                    : id.equals("jormungandr") ? String.format(java.util.Locale.ROOT, "tp @a %d.5 214 26 180 38", x)
                    : String.format(java.util.Locale.ROOT, "tp @a %d.5 %.1f %.1f 180 12", x, 201.5 + d * 0.2, d);
            String angle = id.equals("bull_shark") ? String.format(java.util.Locale.ROOT, "tp @a %d.5 202 11 160 28", x + 5)
                    : id.equals("jormungandr") ? String.format(java.util.Locale.ROOT, "tp @a %d.5 210 20 135 30", x + 20)
                    : String.format(java.util.Locale.ROOT, "tp @a %.1f %.1f %.1f 135 10", x + d * 0.7, 201.0 + d * 0.15, d * 0.7);
            steps.add(() -> cmd(mc, front));
            steps.add(() -> shot(mc, "boss_" + id));
            steps.add(() -> cmd(mc, angle));
            steps.add(() -> shot(mc, "boss_" + id + "_angle"));
            steps.add(() -> cmd(mc, front));
            String move = moves[i];
            steps.add(() -> { cmd(mc, "execute positioned " + x + ".5 200 0.5 run ragnarok boss animate " + move); nextWait = 14; });
            steps.add(() -> shot(mc, "boss_" + id + "_" + move));
            if (i >= 10) {
                steps.add(() -> { cmd(mc, "execute positioned " + x + ".5 200 0.5 run ragnarok boss animate stagger"); nextWait = 16; });
                steps.add(() -> shot(mc, "boss_" + id + "_stagger"));
            }
            steps.add(() -> { cmd(mc, "execute positioned " + x + ".5 200 0.5 run ragnarok boss animate attack"); nextWait = 5; });
            steps.add(() -> shot(mc, "boss_" + id + "_attack"));
            steps.add(() -> cmd(mc, "kill @e[tag=vividlands_ragnarok.boss." + id + "]"));
        }
        steps.add(mc::stop);
    }

    /** The ancient-civilization sets on armour stands in rows of seven, close-ups of each, and a transmog check. */
    private static void planAncient(Minecraft mc) {
        java.util.List<String> ids = new ArrayList<>();
        for (var s : com.vividlands.ragnarok.armor.AncientSets.ALL) ids.add(s.id());
        steps.add(() -> {
            for (String c : new String[]{"gamerule doDaylightCycle false", "time set 6000", "weather clear",
                    "gamerule doMobSpawning false", "gamerule vividlandsBossSpawning false", "gamemode spectator @a",
                    "tp @a 0.5 202 8.5 180 0"}) cmd(mc, c);
            mc.options.hideGui = true;
        });
        int rows = (ids.size() + 6) / 7;
        for (int row = 0; row < rows; row++) {
            int z = row * 12;
            int rr = row;
            steps.add(() -> {
                cmd(mc, String.format(java.util.Locale.ROOT, "fill -12 199 %d 12 199 %d minecraft:smooth_stone", z - 5, z + 6));
                for (int k = 0; k < 7 && rr * 7 + k < ids.size(); k++) {
                    cmd(mc, stand(ids.get(rr * 7 + k), -9 + k * 3 + 0.5, z + 0.5, 180));
                }
            });
            steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a 0.5 201.6 %.1f 0 6", z - 9.5)));
            steps.add(() -> shot(mc, "ancient_row" + rr + "_front"));
            steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a 0.5 201.6 %.1f 180 6", z + 10.5)));
            steps.add(() -> shot(mc, "ancient_row" + rr + "_back"));
        }
        // close-ups: every set from the front, every other from the back
        for (int i = 0; i < ids.size(); i++) {
            String id = ids.get(i);
            double x = -9 + (i % 7) * 3 + 0.5;
            int z = (i / 7) * 12;
            boolean back = i % 2 == 0 || id.equals("agamemnon");
            steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a %.1f 201.2 %.1f 0 4", x, z - 2.6)));
            steps.add(() -> shot(mc, "ancient_" + id + "_front"));
            if (back) {
                steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a %.1f 201.2 %.1f 180 4", x, z + 3.6)));
                steps.add(() -> shot(mc, "ancient_" + id + "_back"));
            }
        }
        // Agamemnon's mask up close, and at night to see the glowing eyes
        int az = (ids.indexOf("agamemnon") / 7) * 12;
        double ax = -9 + (ids.indexOf("agamemnon") % 7) * 3 + 0.5;
        steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a %.1f 200.15 %.1f 0 0", ax, az - 0.9)));
        steps.add(() -> shot(mc, "ancient_agamemnon_mask"));
        steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a %.1f 200.2 %.1f 47 2", ax + 1.2, az - 0.6)));
        steps.add(() -> shot(mc, "ancient_agamemnon_mask_side"));
        steps.add(() -> cmd(mc, "time set 18000"));
        steps.add(() -> cmd(mc, String.format(java.util.Locale.ROOT, "tp @a %.1f 200.15 %.1f 0 0", ax, az - 0.9)));
        steps.add(() -> shot(mc, "ancient_agamemnon_mask_night"));
        steps.add(() -> cmd(mc, "time set 6000"));
        // transmog: plain iron, diamond and leather pieces glamoured to look like other sets, beside unglamoured copies
        steps.add(() -> {
            int z = -20;
            cmd(mc, String.format(java.util.Locale.ROOT, "fill -12 199 %d 12 199 %d minecraft:smooth_stone", z - 5, z + 6));
            String[][] looks = {{"iron", "agamemnon"}, {"diamond", "egyptian"}, {"leather", "samurai"}, {"netherite", "mycenaean"}};
            for (int k = 0; k < looks.length; k++) {
                String m = looks[k][0], look = "vividlands_ragnarok:" + looks[k][1] + "_";
                cmd(mc, String.format(java.util.Locale.ROOT,
                        "summon minecraft:armor_stand %.1f 200 %d.5 {ShowArms:1b,NoBasePlate:1b,NoGravity:1b,Rotation:[180f,0f],ArmorItems:["
                                + "{id:\"minecraft:%s_boots\",Count:1b,tag:{VividGlamour:\"%sboots\"}},"
                                + "{id:\"minecraft:%s_leggings\",Count:1b,tag:{VividGlamour:\"%sleggings\"}},"
                                + "{id:\"minecraft:%s_chestplate\",Count:1b,tag:{VividGlamour:\"%schestplate\"}},"
                                + "{id:\"minecraft:%s_helmet\",Count:1b,tag:{VividGlamour:\"%shelmet\"}}]}",
                        -9 + k * 6 + 0.5, z, m, look, m, look, m, look, m, look));
                cmd(mc, String.format(java.util.Locale.ROOT,
                        "summon minecraft:armor_stand %.1f 200 %d.5 {ShowArms:1b,NoBasePlate:1b,NoGravity:1b,Rotation:[180f,0f],ArmorItems:["
                                + "{id:\"minecraft:%s_boots\",Count:1b},{id:\"minecraft:%s_leggings\",Count:1b},"
                                + "{id:\"minecraft:%s_chestplate\",Count:1b},{id:\"minecraft:%s_helmet\",Count:1b}]}",
                        -9 + k * 6 + 2.5, z, m, m, m, m));
            }
        });
        steps.add(() -> cmd(mc, "tp @a 0.5 201.6 -29.5 0 6"));
        steps.add(() -> shot(mc, "glamour_row"));
        steps.add(() -> cmd(mc, "tp @a -7.5 201.2 -23.6 0 4"));
        steps.add(() -> shot(mc, "glamour_iron_as_agamemnon"));
        // a glamoured piece on the player, seen in third person
        steps.add(() -> {
            cmd(mc, "gamemode creative @a");
            cmd(mc, "tp @a 0.5 200 -34.5 0 0");
            cmd(mc, "item replace entity @a armor.chest with minecraft:iron_chestplate{VividGlamour:\"vividlands_ragnarok:agamemnon_chestplate\"}");
            cmd(mc, "item replace entity @a armor.head with minecraft:iron_helmet{VividGlamour:\"vividlands_ragnarok:agamemnon_helmet\"}");
            mc.options.setCameraType(net.minecraft.client.CameraType.THIRD_PERSON_FRONT);
        });
        steps.add(() -> shot(mc, "glamour_player"));
        steps.add(() -> mc.options.setCameraType(net.minecraft.client.CameraType.FIRST_PERSON));
        steps.add(mc::stop);
    }

    /** The five classes: each casts its four abilities at a row of zombies, with the HUD visible. */
    private static void planClasses(Minecraft mc) {
        steps.add(() -> {
            for (String c : new String[]{"gamerule doDaylightCycle false", "time set 6000", "weather clear", "gamerule doMobSpawning false",
                    "gamerule vividlandsBossSpawning false", "difficulty normal", "gamemode creative @a",
                    "fill -16 199 -8 16 199 24 minecraft:grass_block", "fill -16 200 -8 16 215 24 minecraft:air",
                    "tp @a 0.5 200 0.5 0 12"}) cmd(mc, c);
            mc.options.hideGui = false;
        });
        steps.add(() -> { cmd(mc, "execute as @p run ragnarok class set huntsman 12"); nextWait = 20; });
        steps.add(() -> shot(mc, "class_hud_level12"));
        String[] ids = {"berserker", "valkyrie", "huntsman", "volva", "ulfhednar"};
        for (String id : ids) {
            steps.add(() -> {
                cmd(mc, "kill @e[type=minecraft:zombie]");
                cmd(mc, "kill @e[type=minecraft:wolf]");
                cmd(mc, "kill @e[type=minecraft:arrow]");
                for (int i = 0; i < 6; i++) {
                    cmd(mc, String.format(java.util.Locale.ROOT,
                            "summon minecraft:zombie %.1f 200 %.1f {NoAI:1b,PersistenceRequired:1b,Health:200f,Attributes:[{Name:\"generic.max_health\",Base:200d}]}",
                            -5.0 + i * 2, 7.5 + (i % 2)));
                }
                cmd(mc, "tp @a 0.5 200 0.5 0 12");
                cmd(mc, "execute as @p run ragnarok class set " + id + " 50");
                cmd(mc, "execute as @p run ragnarok class ready");
                nextWait = 20;
            });
            steps.add(() -> shot(mc, "class_" + id + "_hud"));
            for (int slot = 1; slot <= 4; slot++) {
                int s = slot;
                steps.add(() -> {
                    cmd(mc, "tp @a 0.5 200 0.5 0 12");
                    cmd(mc, "execute as @p at @s anchored eyes facing 0.5 201 8 run ragnarok class cast " + s);
                    nextWait = s == 2 && (id.equals("berserker") || id.equals("valkyrie")) ? 8 : 6;
                });
                steps.add(() -> shot(mc, "class_" + id + "_" + s));
            }
            steps.add(() -> { nextWait = 30; });
            steps.add(() -> shot(mc, "class_" + id + "_after"));
            steps.add(() -> cmd(mc, "data get entity @e[type=minecraft:zombie,limit=1,sort=nearest] Health"));
        }
        steps.add(mc::stop);
    }

    /** The Norse UI: class panel, boss bar in both phases, class screen, tooltips and pop-ups. */
    static net.minecraft.world.item.ItemStack testTooltip = net.minecraft.world.item.ItemStack.EMPTY;

    private static void planUi(Minecraft mc) {
        net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback.EVENT.register((g, d) -> {
            if (!testTooltip.isEmpty()) g.renderTooltip(mc.font, testTooltip, g.guiWidth() / 2 - 150, 90);
        });
        steps.add(() -> {
            for (String c : new String[]{"gamerule doDaylightCycle false", "time set 6000", "weather clear", "gamerule doMobSpawning false",
                    "gamerule vividlandsBossSpawning false", "difficulty peaceful", "gamemode creative @a",
                    "fill -20 199 -8 20 199 40 minecraft:grass_block", "tp @a 0.5 200 0.5 0 5"}) cmd(mc, c);
            mc.options.hideGui = false;
        });
        steps.add(() -> { cmd(mc, "execute as @p run ragnarok class set huntsman 26"); nextWait = 20; });
        steps.add(() -> { cmd(mc, "execute as @p run ragnarok class xp 900"); nextWait = 30; });
        steps.add(() -> shot(mc, "ui_levelup_toast"));
        steps.add(() -> { cmd(mc, "execute as @p at @s anchored eyes facing 0.5 201 8 run ragnarok class cast 2"); nextWait = 10; });
        steps.add(() -> shot(mc, "ui_class_panel_cooldown"));
        steps.add(() -> {
            cmd(mc, "item replace entity @p armor.head with vividlands_ragnarok:dacian_helmet");
            cmd(mc, "item replace entity @p armor.chest with vividlands_ragnarok:dacian_chestplate");
            cmd(mc, "item replace entity @p armor.legs with vividlands_ragnarok:dacian_leggings");
            cmd(mc, "item replace entity @p armor.feet with vividlands_ragnarok:dacian_boots");
            cmd(mc, "ragnarok boss summon cave_lion 0.5 200 16.5");
            nextWait = 40;
        });
        steps.add(() -> shot(mc, "ui_beast_toast_bossbar"));
        steps.add(() -> {
            cmd(mc, "execute as @e[tag=vividlands_ragnarok.boss.cave_lion] run data merge entity @s {NoAI:1b}");
            cmd(mc, "damage @e[tag=vividlands_ragnarok.boss.cave_lion,limit=1] 300 minecraft:generic");
            nextWait = 80;
        });
        steps.add(() -> shot(mc, "ui_bossbar_phase2"));
        steps.add(() -> { ClassClient.actBanner(3); nextWait = 30; });
        steps.add(() -> shot(mc, "ui_act_banner"));
        steps.add(() -> { mc.setScreen(new ClassScreen()); nextWait = 20; });
        steps.add(() -> shot(mc, "ui_class_screen"));
        steps.add(() -> { mc.setScreen(null); testTooltip = new net.minecraft.world.item.ItemStack(
                net.minecraft.core.registries.BuiltInRegistries.ITEM.get(new net.minecraft.resources.ResourceLocation("vividlands_ragnarok:dacian_helmet"))); nextWait = 10; });
        steps.add(() -> shot(mc, "ui_tooltip_armor"));
        steps.add(() -> { testTooltip = new net.minecraft.world.item.ItemStack(com.vividlands.ragnarok.classes.Classes.RUNES.get(
                com.vividlands.ragnarok.classes.NorseClass.BERSERKER)); nextWait = 10; });
        steps.add(() -> shot(mc, "ui_tooltip_rune"));
        steps.add(() -> { testTooltip = new net.minecraft.world.item.ItemStack(
                net.minecraft.core.registries.BuiltInRegistries.ITEM.get(new net.minecraft.resources.ResourceLocation("vividlands_ragnarok:lion_mane"))); nextWait = 10; });
        steps.add(() -> shot(mc, "ui_tooltip_trophy"));
        steps.add(() -> testTooltip = net.minecraft.world.item.ItemStack.EMPTY);
        steps.add(mc::stop);
    }

    /** The quest book (FTB Quests): opens a chapter or quest by the id tools/questbook/build_quests.py gave it (reflection). */
    private static void questBook(String key) {
        try {
            byte[] h = java.security.MessageDigest.getInstance("SHA-1").digest(("vividlands:" + key).getBytes(java.nio.charset.StandardCharsets.UTF_8));
            StringBuilder hex = new StringBuilder();
            for (int i = 0; i < 8; i++) hex.append(String.format("%02X", h[i]));
            if (hex.charAt(0) == '0') hex.setCharAt(0, '1');
            long id = Long.parseUnsignedLong(hex.toString(), 16);
            Class.forName("dev.ftb.mods.ftbquests.client.ClientQuestFile").getMethod("openBookToQuestObject", long.class).invoke(null, id);
        } catch (Exception e) {
            Ragnarok.LOG.warn("render test: could not open the quest book", e);
        }
    }

    private static void planQuests(Minecraft mc) {
        steps.add(() -> {
            for (String c : new String[]{"gamerule doDaylightCycle false", "time set 6000", "weather clear", "gamerule doMobSpawning false",
                    "gamerule vividlandsBossSpawning false", "gamemode creative @a", "tp @a 0.5 200 0.5 0 5", "ragnarok questcheck"}) cmd(mc, c);
            mc.options.hideGui = false;
            nextWait = 60;
        });
        steps.add(() -> { cmd(mc, "effect give @a minecraft:slow_falling 600 0 true"); nextWait = 20; });
        String[] views = {"chapter/prologue", "quest/p1", "chapter/chapter1", "quest/cave_bear", "chapter/chapter2", "chapter/forge",
                "chapter/armory", "chapter/paths", "chapter/hall"};
        for (String v : views) {
            steps.add(() -> { mc.setScreen(null); questBook(v); nextWait = 40; });
            steps.add(() -> shot(mc, "quests_" + v.replace('/', '_')));
        }
        steps.add(mc::stop);
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
                String scene = System.getProperty("vividlands.rendertest.scene", "armor");
                if ("bosses".equals(scene)) planBosses(mc);
                else if ("ancient".equals(scene)) planAncient(mc);
                else if ("classes".equals(scene)) planClasses(mc);
                else if ("ui".equals(scene)) planUi(mc);
                else if ("quests".equals(scene)) planQuests(mc);
                else plan(mc);
                Ragnarok.LOG.info("render test: in world, {} steps", steps.size());
            }
            return;
        }
        if (--wait > 0 || steps.isEmpty()) return;
        steps.remove(0).run();
        wait = nextWait > 0 ? nextWait : 50;
        nextWait = 0;                      // let chunks load and the camera settle between steps
    }
}
