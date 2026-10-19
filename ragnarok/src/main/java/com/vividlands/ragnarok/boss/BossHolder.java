package com.vividlands.ragnarok.boss;

/** Added to every entity by a mixin: the id of the boss it is, or null (both sides; the client gets it in a packet). */
public interface BossHolder {
    String vlr$boss();

    void vlr$setBoss(String id);
}
