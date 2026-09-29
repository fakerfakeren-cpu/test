package com.rimeheart.client.render;

import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.EyesLayer;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;

/** Full-bright emissive pass using a *_glow texture. */
public class GlowLayer<S extends EntityRenderState, M extends EntityModel<S>> extends EyesLayer<S, M> {
    private final RenderType type;

    public GlowLayer(RenderLayerParent<S, M> parent, Identifier glowTexture) {
        super(parent);
        this.type = RenderTypes.eyes(glowTexture);
    }

    @Override
    public RenderType renderType() {
        return type;
    }
}
