"""
@UnrealClaude Script
@Description: Diagnostic - check material nodes, MPC defaults, and PostProcessVolume blendables
"""
import unreal

# === Material structure ===
mat_path = '/Game/GamePlay/Materials/M_PoisonCircle_PP'
mat = unreal.EditorAssetLibrary.load_asset(mat_path)
if mat:
    print('=== MATERIAL INFO ===')
    print('MaterialDomain: {}'.format(mat.get_editor_property('material_domain')))
    print('BlendMode: {}'.format(mat.get_editor_property('blend_mode')))
    
    exps = mat.get_editor_property('expressions')
    if exps:
        print('Expressions ({}):'.format(len(exps)))
        for exp in exps:
            exp_class = exp.get_class().get_name()
            line = '  [{}] '.format(exp_class)
            
            if exp_class == 'MaterialExpressionCollectionParameter':
                try:
                    col = exp.get_editor_property('collection')
                    line += 'Collection={} '.format(col.get_name() if col else 'None')
                except: pass
                try:
                    pn = exp.get_editor_property('parameter_name')
                    line += 'ParamName={} '.format(pn)
                except: pass
            
            elif exp_class == 'MaterialExpressionSceneTexture':
                try:
                    sti = exp.get_editor_property('scene_texture_id')
                    line += 'SceneTextureId={} '.format(sti)
                except: pass
            
            elif exp_class in ['MaterialExpressionConstant', 'MaterialExpressionScalarParameter']:
                try:
                    v = exp.get_editor_property('r')
                    line += 'Value={} '.format(v)
                except: pass
            
            elif exp_class == 'MaterialExpressionConstant3Vector':
                try:
                    c = exp.get_editor_property('constant')
                    line += 'Color=({},{},{}) '.format(c.r, c.g, c.b)
                except: pass
            
            elif exp_class == 'MaterialExpressionComponentMask':
                try:
                    line += 'R={},G={},B={},A={} '.format(
                        exp.get_editor_property('r'),
                        exp.get_editor_property('g'),
                        exp.get_editor_property('b'),
                        exp.get_editor_property('a'))
                except: pass
            
            print(line)
    else:
        print('NO EXPRESSIONS! Material is empty!')
    
    print('=== EMISSIVE COLOR CONNECTION ===')
    try:
        emissive = mat.get_editor_property('emissive_color')
        if emissive and emissive.get_editor_property('expression'):
            connected_exp = emissive.get_editor_property('expression')
            print('EmissiveColor connected to: {}'.format(connected_exp.get_class().get_name()))
        else:
            print('EmissiveColor: NOT CONNECTED!')
    except Exception as e:
        print('EmissiveColor check failed: {}'.format(e))
else:
    print('MATERIAL NOT FOUND!')

# === MPC defaults ===
print('=== MPC DEFAULTS ===')
mpc_path = '/Game/GamePlay/Materials/MPC_PoisonCircle'
mpc = unreal.EditorAssetLibrary.load_asset(mpc_path)
if mpc:
    scalars = mpc.get_editor_property('scalar_parameters')
    vectors = mpc.get_editor_property('vector_parameters')
    print('Scalars ({}):'.format(len(scalars)))
    for s in scalars:
        print('  {} = {}'.format(
            s.get_editor_property('parameter_name'),
            s.get_editor_property('default_value')))
    print('Vectors ({}):'.format(len(vectors)))
    for v in vectors:
        name = v.get_editor_property('parameter_name')
        val = v.get_editor_property('default_value')
        print('  {} = ({}, {}, {}, {})'.format(name, val.r, val.g, val.b, val.a))
else:
    print('MPC NOT FOUND!')

# === PostProcessVolume ===
print('=== POST PROCESS VOLUME ===')
import unreal.EditorLevelLibrary as ell
actors = ell.get_all_level_actors()
for a in actors:
    if a.get_class().get_name() == 'PostProcessVolume':
        print('Actor: {}'.format(a.get_actor_label()))
        print('  Location: {}'.format(a.get_actor_location()))
        print('  bUnbound: {}'.format(a.get_editor_property('b_unbound')))
        try:
            blendables = a.get_editor_property('blendables')
            if blendables:
                print('  Blendables count: {}'.format(len(blendables)))
                for i, b in enumerate(blendables):
                    try:
                        mat_ref = b.get_editor_property('material')
                        weight = b.get_editor_property('weight')
                        print('  [{}] Material={}, Weight={}'.format(
                            i,
                            mat_ref.get_name() if mat_ref else 'None',
                            weight))
                    except Exception as e:
                        print('  [{}] Error: {}'.format(i, e))
            else:
                print('  Blendables: EMPTY')
        except Exception as e:
            print('  Blendables error: {}'.format(e))
        break

print('=== DIAGNOSTIC COMPLETE ===')
