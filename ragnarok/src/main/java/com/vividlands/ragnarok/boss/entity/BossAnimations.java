package com.vividlands.ragnarok.boss.entity;

import net.minecraft.world.entity.Entity;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

/**
 * The animation set every pack boss model has (animations/entity/boss/<id>.animation.json):
 * looping idle / walk / swim, and one-shot moves started from the server when the boss uses an ability.
 */
public final class BossAnimations {
    public static final String[] MOVES = {"attack", "roar", "slam", "charge", "leap", "roll", "throw", "hurt",
            "combo", "breath", "grab", "spin", "swoop", "stagger"};
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.boss.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.boss.walk");
    private static final RawAnimation RUN = RawAnimation.begin().thenLoop("animation.boss.run");

    private BossAnimations() {
    }

    public static <T extends Entity & GeoEntity> void register(T entity, AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<GeoAnimatable>(entity, "move", 6, state -> {
            if (state.isMoving()) {
                double speed = entity.getDeltaMovement().horizontalDistance();
                return state.setAndContinue(speed > 0.18 ? RUN : WALK);
            }
            return state.setAndContinue(IDLE);
        }));
        AnimationController<GeoAnimatable> action = new AnimationController<>(entity, "action", 2, state -> PlayState.STOP);
        for (String m : MOVES) action.triggerableAnim(m, RawAnimation.begin().thenPlay("animation.boss." + m));
        controllers.add(action);
    }
}
