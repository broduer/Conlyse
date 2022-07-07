import {
    Box, Divider, Grid,
    IconButton, List, ListItem,
    Typography
} from "@mui/material";
import {Delete, ExpandMore} from "@mui/icons-material";
import {getDrawingLevelName} from "../../utils";
import ColorsSelectorEditor from "./drawing_editor/colors_selector_editor";
import RadiusChanger from "./drawing_editor/radius_changer";
import StrokeWidthChanger from "./drawing_editor/stroke_width_changer";
import LayerChanger from "./drawing_editor/layer_changer";
import * as React from "react"
export default function DrawingsEditor({drawings, setDrawings}){

    const deleteDrawing = (index) => {
        let cp = [...drawings]
        cp.splice(index, 1)
        setDrawings(cp)
    }
    if(drawings.length === 0) return (<React.Fragment/>)
    return (
        <Box sx={{
            position: "absolute",
            left: 0,
            bottom: 65,
            margin: 2,
            backgroundColor: "background.paper",
            border: 3,
            borderColor: "primary.main",
            borderRadius: 10,
            maxHeight: "50vh",
            overflow: "auto",
        }}
        >
            <List style={{margin: 3}}>
                {Object.values(drawings).map((drawing, index) => {
                    let name = getDrawingLevelName(drawing["drawingLevel"])
                    return (
                        <React.Fragment key={index}>
                            <ListItem>
                                <Typography>{name}</Typography>
                                <Grid container
                                      columnSpacing={3}
                                      direction={"row"}
                                      alignItems={"center"}
                                      ml={2}
                                      mr={2}
                                >
                                    <Grid item>
                                        <ColorsSelectorEditor index={index} drawings={drawings} setDrawing={setDrawings}/>
                                    </Grid>
                                    <Grid item>
                                        {drawing["drawingLevel"] === 2 ? <RadiusChanger index={index} drawings={drawings} setDrawings={setDrawings} /> : undefined}
                                    </Grid>
                                    <Grid item>
                                        <StrokeWidthChanger index={index} drawings={drawings} setDrawings={setDrawings}/>
                                    </Grid>
                                    <Grid item>
                                        <LayerChanger index={index} drawings={drawings} setDrawings={setDrawings}/>
                                    </Grid>
                                </Grid>
                                <IconButton size="small" onClick={() => deleteDrawing(index)}><Delete color={"error"}/></IconButton>
                            </ListItem>
                            <Divider/>
                        </React.Fragment>
                    )
                })}
            </List>
        </Box>
    )
}