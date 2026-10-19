package com.vividlands.ragnarok.boss;

/** Added to every entity by a mixin: the id of the boss it is, or null (both sides; the client gets it in a packet). */
public interface BossHolder {
    String vlr$boss();

    void vlr$setBoss(String id);

    /** True when the creature's own mod scales it (Fossils and Archeology), so the pack doesn't scale it again. */
    boolean vlr$nativeScale();

    void vlr$setNativeScale(boolean value);
}
