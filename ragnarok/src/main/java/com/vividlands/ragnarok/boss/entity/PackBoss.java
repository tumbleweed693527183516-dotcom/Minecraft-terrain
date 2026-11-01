package com.vividlands.ragnarok.boss.entity;

/** The pack's own animated bosses: abilities call {@link #playMove} to start a one-shot animation. */
public interface PackBoss {
    void playMove(String move);
}
