package com.vividlands;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Sharpened log tip for palisade walls. */
public class StakeBlock extends Block {
    private static final VoxelShape SHAPE = Shapes.or(
            Block.box(2, 0, 2, 14, 9, 14), Block.box(4, 9, 4, 12, 13, 12), Block.box(6, 13, 6, 10, 16, 10));

    public StakeBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    @SuppressWarnings("deprecation")
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }
}
