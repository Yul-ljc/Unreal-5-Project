"""
@UnrealClaude Script
@Description: Diag v3 - MPC defaults and PP volume blendables
"""
import unreal

# 1. Material basic info
mat_path = '/Game/GamePlay/Materials/M_PoisonCircle_PP'
mat = unreal.EditorAssetLibrary.load_asset(mat_path)
print('1_Domain:', mat.get_editor_property('material_domain'))
print('2_BlendMode:', mat.get_editor_property('blend_mode'))
print('3_NumExpressions:', len(mat.get_editor_property('expressions')))

# 2. MPC
mpc = unreal.EditorAssetLibrary.load_asset('/Game/GamePlay/Materials/MPC_PoisonCircle')
print('4_MPC_Scalars:')
for s in mpc.get_editor_property('scalar_parameters'):
    print('  ', s.get_editor_property('parameter_name'), '=', s.get_editor_property('default_value'))
print('5_MPC_Vectors:')
for v in mpc.get_editor_property('vector_parameters'):
    val = v.get_editor_property('default_value')
    print('  ', v.get_editor_property('parameter_name'), '= ({:.1f}, {:.1f}, {:.1f}, {:.1f})'.format(val.r, val.g, val.b, val.a))

# 3. PostProcessVolume
import unreal.EditorLevelLibrary as ell
for a in ell.get_all_level_actors():
    if a.get_class().get_name() == 'PostProcessVolume':
        print('6_PPV_bUnbound:', a.get_editor_property('b_unbound'))
        bls = a.get_editor_property('blendables')
        if bls:
            print('7_Blendables_count:', len(bls))
            for i, b in enumerate(bls):
                mref = b.get_editor_property('material')
                w = b.get_editor_property('weight')
                print('  [{}] mat={}, weight={}'.format(i, mref.get_name() if mref else 'None', w))
        else:
            print('7_Blendables: EMPTY')
        break

print('DONE')
