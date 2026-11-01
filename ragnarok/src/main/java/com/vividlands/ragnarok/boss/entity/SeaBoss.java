package com.vividlands.ragnarok.boss.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WaterBoundPathNavigation;
import net.minecraft.world.entity.animal.WaterAnimal;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.util.GeckoLibUtil;

/** A boss that lives in the sea (the bull shark, later Jormungandr). */
public class SeaBoss extends WaterAnimal implements GeoEntity, PackBoss {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public SeaBoss(EntityType<? extends WaterAnimal> type, Level level) {
        super(type, level);
        moveControl = new SmoothSwimmingMoveControl(this, 85, 10, 0.06f, 0.1f, true);
        lookControl = new SmoothSwimmingLookControl(this, 10);
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new WaterBoundPathNavigation(this, level);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(5, new RandomSwimmingGoal(this, 1.0, 10));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
    }

    @Override
    public void travel(Vec3 input) {
        if (isControlledByLocalInstance() && isInWater()) {
            moveRelative(getSpeed(), input);
            move(net.minecraft.world.entity.MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(0.9));
        } else {
            super.travel(input);
        }
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public void playMove(String move) {
        triggerAnim("action", move);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        BossAnimations.register(this, controllers);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
