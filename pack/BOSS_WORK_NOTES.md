# Boss work in progress (paused 2026-10-31)

User's latest asks: 20 animal bosses in Chapter 1, 5 mythological in Chapter 2; ocean fights limited (only Bull Shark +
Jormungandr) plus a sea blessing; final bosses keep the blocky style but look more like final bosses; Jormungandr
longer and more snake-like; moves inspired by other games' boss fights (not copied); then open every boss in
Blockbench in Animate mode for the user. Skip GitHub game tests unless asked; check with tools/boss_preview.py.

## Done (not yet committed to main)
- Move system (Java, ragnarok/.../boss):
  - BossFight: phase 2 at half health (roar, knockback, 2 s invulnerable, learns BossDef.phase2 moves); stagger/poise
    (7% max HP in a few seconds -> stunned 70 ticks, "stagger" anim); punish window (+50% damage while stunned);
    sea blessing (Conduit Power + Dolphin's Grace near aquatic bosses); marker()/DANGER telegraph rings; groundAt().
  - New abilities: Combo, Breath (FIRE/FROST/VENOM/SHADOW), HazardRain (ICICLE/ROCK/FIRE/LIGHTNING), Grab
    (SQUEEZE/CARRY), Spin (dizzy after), Swoop (flyers). Slam now telegraphs its area.
  - FlyingBoss entity + BossEntities.fly(); BossDef.phase2(); BossAnimations.MOVES += combo, breath, grab, spin, swoop, stagger.
- Models (mobkit, Minecraft style): tools/ch1_models.py (dire_wolf, cave_lion, steppe_bison, ground_sloth, glyptodon,
  terror_bird, haast_eagle, komodo, anaconda, walrus); tools/ch2_models.py (sleipnir + fenrir upgraded, jormungandr
  26 segments with glowing venom line, new garmr and fafnir). mobkit gained plates/feather styles, stripes/spots/
  lateral/coins marks, glowing scars.
- Animations: tools/boss_anims2.py writes all 25 bosses (new rigs: bird, eagle, serpent, dragon; every boss has the
  new moves). Run order: ch1_models.py, ch2_models.py, boss_anims2.py.

## Still to do
1. Bosses.java: imports for the new abilities; defs for the 10 new animals + garmr + fafnir; phase-2 moves and new
   moves for all; unlock order (plan: bear, dire wolf | elk, bison | hippo, terror bird | croc, komodo, glyptodon |
   silverback, cave lion, anaconda | saber, sloth, rhino | eagle, walrus | elephant, bull shark | mammoth last).
   Chapter 2 order: sleipnir -> garmr -> fafnir -> jormungandr -> fenrir.
2. BossEntities: land(...) for the 9 land animals + garmr + fafnir, fly("haast_eagle"); GLOWING set += garmr, fafnir.
3. Trophies + icons + lang (boss_data.py): new trophy items, boss names, entity names,
   boss.vividlands_ragnarok.staggered / grabbed messages.
4. Push, check the Build workflow compiles.
5. Load all 25 bosses into Blockbench (Animate mode), saving .bbmodel copies to tools/models/bosses.
6. MOD_LOG section, update the vivid-lands-boss-builder skill.
