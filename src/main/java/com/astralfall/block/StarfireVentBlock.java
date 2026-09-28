package com.astralfall.block;

import com.astralfall.util.FX;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** Trap: erupts with a column of starfire when stepped on, and every so often on its own. */
public class StarfireVentBlock extends Block {
    public static final MapCodec<StarfireVentBlock> CODEC = simpleCodec(StarfireVentBlock::new);
    public static final BooleanProperty ACTIVE = BooleanProperty.create("active");

    public StarfireVentBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(ACTIVE, false));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(ACTIVE);
    }

    @Override
    public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        if (level instanceof ServerLevel server && !state.getValue(ACTIVE) && entity instanceof LivingEntity) {
            erupt(server, pos, state);
        }
    }

    @Override
    protected void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (!state.getValue(ACTIVE) && random.nextInt(3) == 0) erupt(level, pos, state);
    }

    private void erupt(ServerLevel level, BlockPos pos, BlockState state) {
        level.setBlock(pos, state.setValue(ACTIVE, true), 3);
        level.scheduleTick(pos, this, 40);
        Vec3 c = Vec3.atCenterOf(pos).add(0, 0.6, 0);
        for (int i = 0; i < 4; i++) {
            FX.burst(level, ParticleTypes.FLAME, c.x, c.y + i * 0.6, c.z, 12, 0.2, 0.3, 0.2, 0.03);
        }
        FX.burst(level, ParticleTypes.LAVA, c, 6, 0.2, 0.2);
        FX.burst(level, ParticleTypes.LARGE_SMOKE, c.x, c.y + 2.5, c.z, 6, 0.3, 0.3, 0.3, 0.02);
        level.playSound(null, pos, SoundEvents.BLAZE_SHOOT, SoundSource.BLOCKS, 1.0f, 0.7f);
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(pos).inflate(0.2, 0, 0.2).expandTowards(0, 3, 0))) {
            e.igniteForSeconds(4);
            e.hurtServer(level, level.damageSources().inFire(), 4.0f);
        }
    }

    @Override
    protected void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (state.getValue(ACTIVE)) level.setBlock(pos, state.setValue(ACTIVE, false), 3);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(state.getValue(ACTIVE) ? 1 : 8) == 0) {
            level.addParticle(state.getValue(ACTIVE) ? ParticleTypes.FLAME : ParticleTypes.SMOKE, pos.getX() + 0.3 + random.nextDouble() * 0.4, pos.getY() + 1.02, pos.getZ() + 0.3 + random.nextDouble() * 0.4, 0, 0.06, 0);
        }
    }
}
