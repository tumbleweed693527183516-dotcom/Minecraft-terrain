package com.vividlands.ragnarok.mixin;

import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.GoalSelector;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Lets the boss code add its fight goal to any mob (from any mod). */
@Mixin(Mob.class)
public interface MobGoalsAccessor {
    @Accessor("goalSelector")
    GoalSelector vlr$goals();
}
