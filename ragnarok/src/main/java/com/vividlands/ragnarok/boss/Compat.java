package com.vividlands.ragnarok.boss;

import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.Mob;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Small, optional hooks into the creature mods the bosses are built on, found by name at runtime so none of those
 * mods is needed to build (or run) this one. Every call quietly does nothing when the method isn't there.
 *  - Naturalist bears sleep: setSleeping(false)
 *  - Fossils and Archeology: grown to adult (setAgeInDays), never hungry (setHunger), never asleep
 *    (sleepSystem.setSleeping), attack animation (startAttack)
 */
final class Compat {
    private static final Map<String, Method> METHODS = new ConcurrentHashMap<>();
    private static final Method NONE;

    static {
        try {
            NONE = Compat.class.getDeclaredMethod("none");
        } catch (NoSuchMethodException e) {
            throw new IllegalStateException(e);
        }
    }

    private Compat() {
    }

    @SuppressWarnings("unused")
    private static void none() {
    }

    private static Method find(Class<?> c, String name, Class<?>... args) {
        String key = c.getName() + "#" + name + args.length;
        Method m = METHODS.computeIfAbsent(key, k -> {
            for (Class<?> k2 = c; k2 != null && k2 != Object.class; k2 = k2.getSuperclass()) {
                try {
                    Method found = k2.getDeclaredMethod(name, args);
                    found.setAccessible(true);
                    return found;
                } catch (NoSuchMethodException | RuntimeException ignored) {
                    // try the superclass
                }
            }
            return NONE;
        });
        return m == NONE ? null : m;
    }

    static Object call(Object o, String name, Class<?>[] types, Object... args) {
        if (o == null) return null;
        Method m = find(o.getClass(), name, types);
        if (m == null) return null;
        try {
            return m.invoke(o, args);
        } catch (ReflectiveOperationException | RuntimeException e) {
            return null;
        }
    }

    private static Object field(Object o, String name) {
        for (Class<?> c = o.getClass(); c != null && c != Object.class; c = c.getSuperclass()) {
            try {
                Field f = c.getDeclaredField(name);
                f.setAccessible(true);
                return f.get(o);
            } catch (NoSuchFieldException ignored) {
                // superclass
            } catch (ReflectiveOperationException | RuntimeException e) {
                return null;
            }
        }
        return null;
    }

    /** First spawn: grown up and fed. */
    static void grownUp(Mob mob) {
        if (mob instanceof AgeableMob a) a.setAge(0);
        Object adult = call(mob, "isAdult", new Class<?>[0]);
        for (int i = 0; i < 400 && Boolean.FALSE.equals(adult); i++) {
            Object days = call(mob, "getAgeInDays", new Class<?>[0]);
            if (!(days instanceof Integer d)) break;
            call(mob, "setAgeInDays", new Class<?>[]{int.class}, d + 1);
            adult = call(mob, "isAdult", new Class<?>[0]);
        }
        keepAwake(mob);
    }

    /** Once a second: awake and fed (sleeping or starving bosses would be no fight at all). */
    static void keepAwake(Mob mob) {
        call(mob, "setSleeping", new Class<?>[]{boolean.class}, false);
        Object sleep = field(mob, "sleepSystem");
        if (sleep != null) call(sleep, "setSleeping", new Class<?>[]{boolean.class}, false);
        Object max = call(mob, "getMaxHunger", new Class<?>[0]);
        if (max instanceof Integer m) call(mob, "setHunger", new Class<?>[]{int.class}, m);
        call(mob, "setSitting", new Class<?>[]{boolean.class}, false);
    }

    /** Plays the creature's own attack animation where the mod has one we can trigger. */
    static void attackAnimation(Mob mob) {
        call(mob, "startAttack", new Class<?>[0]);
    }
}
