package com.vividlands.ragnarok.boss;

import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.commands.arguments.coordinates.Vec3Argument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

import java.util.Set;

/**
 * /ragnarok boss summon <id> [pos]   spawn a boss (testing, or for a server event)
 * /ragnarok boss list                all bosses, and whether their creature mod is installed
 * /ragnarok boss progress <player>   which bosses a player has beaten
 * /ragnarok boss forget <player>     reset a player's boss progress
 * /ragnarok boss resetspawns         let every wild / structure boss appear again
 */
final class BossCommands {
    private BossCommands() {
    }

    static void register() {
        CommandRegistrationCallback.EVENT.register((dispatcher, registry, env) -> dispatcher.register(
                Commands.literal("ragnarok").requires(s -> s.hasPermission(2))
                        .then(Commands.literal("boss")
                                .then(Commands.literal("summon")
                                        .then(Commands.argument("id", StringArgumentType.word())
                                                .suggests((c, b) -> SharedSuggestionProvider.suggest(Bosses.DEFS.keySet(), b))
                                                .executes(c -> summon(c, c.getSource().getPosition()))
                                                .then(Commands.argument("pos", Vec3Argument.vec3())
                                                        .executes(c -> summon(c, Vec3Argument.getVec3(c, "pos"))))))
                                .then(Commands.literal("list").executes(BossCommands::list))
                                .then(Commands.literal("progress")
                                        .then(Commands.argument("player", EntityArgument.player()).executes(BossCommands::progress)))
                                .then(Commands.literal("forget")
                                        .then(Commands.argument("player", EntityArgument.player()).executes(c -> {
                                            ServerPlayer p = EntityArgument.getPlayer(c, "player");
                                            BossProgress.get(c.getSource().getServer()).forget(p.getUUID());
                                            c.getSource().sendSuccess(() -> Component.literal("Boss progress cleared for " + p.getScoreboardName()), true);
                                            return 1;
                                        })))
                                .then(Commands.literal("resetspawns").executes(c -> {
                                    BossProgress.get(c.getSource().getServer()).clearSpawned();
                                    c.getSource().sendSuccess(() -> Component.literal("Every boss can appear again"), true);
                                    return 1;
                                })))));
    }

    private static int summon(CommandContext<CommandSourceStack> c, Vec3 pos) {
        String id = StringArgumentType.getString(c, "id");
        BossDef def = Bosses.DEFS.get(id);
        if (def == null) {
            c.getSource().sendFailure(Component.literal("No boss called " + id));
            return 0;
        }
        Mob mob = Bosses.spawn(c.getSource().getLevel(), def, pos);
        if (mob == null) {
            c.getSource().sendFailure(Component.literal("None of " + def.entities + " exist in this game"));
            return 0;
        }
        String type = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(mob.getType()).toString();
        c.getSource().sendSuccess(() -> Component.literal("Summoned boss " + id + " (" + type + ")"), true);
        return 1;
    }

    private static int list(CommandContext<CommandSourceStack> c) {
        for (BossDef d : Bosses.DEFS.values()) {
            String type = Bosses.typeOf(d).map(t -> net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(t).toString())
                    .orElse("MISSING");
            c.getSource().sendSuccess(() -> Component.literal("BOSS " + d.id + " -> " + type), false);
        }
        return Bosses.DEFS.size();
    }

    private static int progress(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer p = EntityArgument.getPlayer(c, "player");
        Set<String> beaten = BossProgress.get(c.getSource().getServer()).defeated(p.getUUID());
        c.getSource().sendSuccess(() -> Component.literal(p.getScoreboardName() + " has beaten " + beaten.size() + ": " + beaten), false);
        return beaten.size();
    }
}
