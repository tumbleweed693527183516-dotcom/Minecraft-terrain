package com.vividlands;

import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;

/** Painted round shield hung on a wall (ladder-style placement, not climbable). */
public class WallShieldBlock extends LadderBlock {
    public WallShieldBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }
}
