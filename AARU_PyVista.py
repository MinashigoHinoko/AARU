import pyvista as pv
import numpy as np

def extractGroupNamesFromObj(objPath):
    """
    Parse the OBJ file and extract group names,
    returning a dict mapping groupId -> groupName.
    """
    groupNameMapping = {}
    groupIdCounter = 0

    with open(objPath, "r") as file:
        for line in file:
            if line.startswith("g "):
                groupName = line.strip().split(" ")[1]
                if groupName not in groupNameMapping.values():
                    groupNameMapping[groupIdCounter] = groupName
                    groupIdCounter += 1
    return groupNameMapping

def loadMesh(modelPath):
    """
    Load the mesh using PyVista's read function.
    """
    return pv.read(modelPath)

def validateMeshForGroupIds(mesh):
    """
    Check whether the loaded mesh has a 'GroupIds' array.
    Returns True if present, otherwise prints a message and returns False.
    """
    if "GroupIds" not in mesh.array_names:
        print("❌ No Group IDs found in PyVista.")
        return False
    return True

def generateColors(uniqueGroupIds):
    """
    Generate and return a dictionary of random RGB colors,
    keyed by groupId.
    """
    return {gId: np.random.rand(3) for gId in uniqueGroupIds}

def prepareSubmeshes(mesh, groupNameMapping):
    """
    For each unique groupId, extract the corresponding submesh (full),
    and then extract the submesh for the 'right half' (points where x>0).
    
    Returns a tuple:
    - submeshesInfo: list of dicts with keys ('gId', 'submesh', 'groupName')
    - rightHalfMeshes: dict keyed by groupId, value = right-half submesh or None
    """
    groupIds = mesh["GroupIds"]
    uniqueGroupIds = np.unique(groupIds)

    submeshesInfo = []
    rightHalfMeshes = {}

    for gId in uniqueGroupIds:
        # Extract the submesh corresponding to the current group ID
        submesh = mesh.extract_cells(groupIds == gId)
        if submesh.n_points == 0:
            # Skip empty submeshes
            rightHalfMeshes[gId] = None
            continue

        # Identify group name
        groupName = groupNameMapping.get(gId, f"Unknown_{gId}")
        
        # Extract right half where x > 0
        rightHalfSubmesh = submesh.extract_points(
            submesh.points[:, 0] > 0,
            adjacent_cells=True
        )
        
        # Store them
        submeshesInfo.append({
            "gId": gId,
            "submesh": submesh,
            "groupName": groupName
        })
        rightHalfMeshes[gId] = (
            rightHalfSubmesh if rightHalfSubmesh.n_points > 0 else None
        )
    
    return submeshesInfo, rightHalfMeshes

def addBaseSubmeshesToPlotter(plotter, submeshesInfo, colors):
    """
    Add each group's base submesh (the entire submesh, uncut) to the plotter
    in its random color. Return a list of the added actor references.
    """
    actors = []
    for info in submeshesInfo:
        gId = info["gId"]
        submesh = info["submesh"]
        groupName = info["groupName"]

        print(f"✅ Adding {groupName} with {submesh.n_cells} faces")
        
        actor = plotter.add_mesh(
            submesh,
            color=colors[gId],
            show_edges=True,
            label=groupName
        )
        actors.append(actor)
    return actors

def createCheckboxCallback(plotter, rightHalfMeshes, groupNameMapping):
    """
    Return a callback function suitable for add_checkbox_button_widget.

    The callback adds/removes the 'right-half' submeshes.
    """
    # We'll keep track of the right-half actors so we can remove them
    rightHalfActors = []

    def checkboxCallback(value):
        """
        Called when the checkbox button is toggled.
        'value' is either True or False, indicating
        checkbox is checked or unchecked.
        """
        nonlocal rightHalfActors

        if value:
            # If checkbox is checked => add the right halves in neon green
            for gId, submesh in rightHalfMeshes.items():
                if submesh:
                    actor = plotter.add_mesh(
                        submesh,
                        color=[0.22, 1.0, 0.08],  # neon green
                        show_edges=False,
                        label=f"{groupNameMapping.get(gId, f'Unknown_{gId}')} (Right Half)"
                    )
                    rightHalfActors.append(actor)
        else:
            # If checkbox is unchecked => remove the right-half actors
            for actor in rightHalfActors:
                plotter.remove_actor(actor)
            rightHalfActors = []

        # Re-render to see the changes
        plotter.render()

    return checkboxCallback

def main():
    modelPath = r"C:\Users\Amir\Documents\untitled.obj"
    
    # Load and validate the mesh
    mesh = loadMesh(modelPath)
    if not validateMeshForGroupIds(mesh):
        return

    # Extract group names
    groupNameMapping = extractGroupNamesFromObj(modelPath)

    # Prepare submeshes for all group IDs and store right-half parts
    submeshesInfo, rightHalfMeshes = prepareSubmeshes(mesh, groupNameMapping)

    # Create a PyVista plotter
    plotter = pv.Plotter()

    # Generate random colors and add base submeshes
    colors = generateColors([info["gId"] for info in submeshesInfo])
    addBaseSubmeshesToPlotter(plotter, submeshesInfo, colors)

    # Add a legend for the base meshes
    plotter.add_legend()

    # Create and add a checkbox callback
    callback = createCheckboxCallback(plotter, rightHalfMeshes, groupNameMapping)
    plotter.add_checkbox_button_widget(
        callback=callback,
        value=False,       # start unchecked
        position=(10, 10), # (x, y) in pixel coords
        size=30
    )

    # Show the interactive window
    plotter.show()

if __name__ == "__main__":
    main()
