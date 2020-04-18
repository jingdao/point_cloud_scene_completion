
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <math.h>
#include <ctype.h>
#include <algorithm>
#define BASE_HASH_CONSTANT 0.618033988
#define STEP_HASH_CONSTANT 0.707106781
#define STRING_HASH_CONSTANT 5381

struct Point {
	float x, y, z;
	unsigned char r, g, b;
};

struct HPoint {
	int xi, yi, zi;
    float x,y,z;
	unsigned char r, g, b;
	int label;
};

struct HPCD {
	int numGrid;
	int numPoints;
	int maxSize;
	float leafSize;
	float minX, minY, minZ, maxX, maxY, maxZ;
	float _minX, _minY, _minZ;
	HPoint** data;
	bool hasColor;
	bool hasLabels;
	bool deepCopy;
};

bool loadPLY(const char* filename, std::vector<Point> *modelVertices) {
	modelVertices->clear();
	FILE* f = fopen(filename, "r");
	if (!f) {
        printf("Cannot find %s\n", filename);
		exit(1);
		return false;
	}
	char buf[256];
	int numVertex, numFace;
	while (fgets(buf, 256, f)) {
		if (sscanf(buf, "element vertex %d", &numVertex) == 1) {
		}
		else if (sscanf(buf, "element face %d", &numFace) == 1) {
		}
		else if (strncmp(buf, "end_header", 10) == 0) {
			for (int i = 0; i<numVertex; i++) {
				fgets(buf, 256, f);
				Point p = {0,0,0,255,255,255};
				if (sscanf(buf, "%f %f %f %hhu %hhu %hhu", &(p.x), &(p.y), &(p.z), &(p.r), &(p.g), &(p.b)) == 6) {
					modelVertices->push_back(p);
				}
				else {
					printf("Error parsing %s\n", filename);
					printf("Line %d: %s\n", i, buf);
					break;
				}
			}
			break;
		}
	}
	fclose(f);
//	printf("Loaded %lu vertices from %s\n", modelVertices->size(), filename);
	return true;
}

void writePLY(const char* filename, std::vector<Point>* pointcloud) {
	FILE* f = fopen(filename, "w");
	if (!f) {
		printf("Cannot write to file: %s\n", filename);
		return;
	}
    fprintf(f, "ply\n"
        "format ascii 1.0\n"
        "element vertex %d\n"
        "property float x\n"
        "property float y\n"
        "property float z\n"
        "property uchar r\n"
        "property uchar g\n"
        "property uchar b\n"
        "end_header\n", pointcloud->size());
    for (int i = 0; i<pointcloud->size(); i++) {
        Point p = pointcloud->at(i);
        fprintf(f, "%f %f %f %d %d %d\n", p.x, p.y,p.z,p.r,p.g,p.b);
	}
	fclose(f);
	printf("Wrote %d points to %s\n", pointcloud->size(), filename);
}

inline int baseHash(int size, int hashKey) {
	return (int)(size*((BASE_HASH_CONSTANT*hashKey) - (int)(BASE_HASH_CONSTANT*hashKey)));
}

inline int stepHash(int size, int hashKey) {
	int res = (int)(size*((STEP_HASH_CONSTANT*hashKey) - (int)(STEP_HASH_CONSTANT*hashKey)));
	//make step size odd since table size is power of 2
	return res % 2 ? res : res + 1;
}

inline int getIntKey(int x, int y, int z) {
	int h = STRING_HASH_CONSTANT;
	h = (h << 5) + h + x;
	h = (h << 5) + h + y;
	h = (h << 5) + h + z;
	if (h < 0)
		return -h;
	else return h;
}

int HPCD_find(HPCD* cloud, int x, int y, int z) {
	int ikey = getIntKey(x, y, z);
	int j = baseHash(cloud->maxSize, ikey);
	int step = stepHash(cloud->maxSize, ikey);
	for (int k = 0; k<cloud->maxSize; k++) {
		HPoint* h = cloud->data[j];
		if (!h) {
			return -1;
		}
		else if (h->xi == x && h->yi == y && h->zi == z){
			return j;
		}
		else {
			j += step;
			j %= cloud->maxSize;
		}
	}
	return -1;
}

HPCD* HPCD_InitFromVector(std::vector<float> *float_data, std::vector<unsigned char> *color_data, float resolution) {
	HPCD* res = new HPCD;
	int totalPoints = float_data->size() / 3;
	res->minX = res->maxX = (*float_data)[0];
	res->minY = res->maxY = (*float_data)[1];
	res->minZ = res->maxZ = (*float_data)[2];
	for (int i = 1; i<totalPoints; i++) {
		float x = float_data->at(i*3);
		float y = float_data->at(i*3 + 1);
		float z = float_data->at(i*3 + 2);
		if (x < res->minX) res->minX = x;
		else if (x > res->maxX) res->maxX = x;
		if (y < res->minY) res->minY = y;
		else if (y > res->maxY) res->maxY = y;
		if (z < res->minZ) res->minZ = z;
		else if (z > res->maxZ) res->maxZ = z;
	}
	
	float minDist = res->maxX - res->minX;
	if (res->maxY - res->minY < minDist)
		minDist = res->maxY - res->minY;
	if (res->maxZ - res->minZ < minDist)
		minDist = res->maxZ - res->minZ;
	res->leafSize = resolution;
	res->numGrid = minDist / res->leafSize;
	res->maxSize = 8;
	while (res->maxSize < 4 * totalPoints)
		res->maxSize *= 2;
	res->data = new HPoint*[res->maxSize]();
	res->deepCopy = true;
	int i, j = 0, k, l = 0;
	float* fp = float_data->data();
	unsigned char* cp = color_data->data();
	res->numPoints = 0;
	for (i = 0; i<totalPoints; i++) {
		float x = fp[j++];
		float y = fp[j++];
		float z = fp[j++];
		unsigned char r = cp[l++];
		unsigned char g = cp[l++];
		unsigned char b = cp[l++];
//		int xi = (int)((x - res->minX) / res->leafSize);
//		int yi = (int)((y - res->minY) / res->leafSize);
//		int zi = (int)((z - res->minZ) / res->leafSize);
        int xi = (int)round(x / res->leafSize);
        int yi = (int)round(y / res->leafSize);
        int zi = (int)round(z / res->leafSize);
		int ikey = getIntKey(xi, yi, zi);
		int key = baseHash(res->maxSize, ikey);
		int step = stepHash(res->maxSize, ikey);
		for (k = 0; k < res->maxSize; k++) {
			HPoint* h = res->data[key];
			if (!h) {
				HPoint* p = new HPoint;
				p->x = x;
				p->y = y;
				p->z = z;
                p->xi = xi;
				p->yi = yi;
				p->zi = zi;
				p->r = r;
				p->g = g;
				p->b = b;
				res->data[key] = p;
				res->numPoints++;
				break;
			}
			else if (h->xi == xi && h->yi == yi && h->zi == zi){
				break;
			}
			else {
				key += step;
				key %= res->maxSize;
			}
		}
	}
//	printf("Processed point cloud (numPoints:%d maxSize:%d leafSize:%f)\n", res->numPoints, res->maxSize, res->leafSize);
//	printf("Bounding box: x:(%.2f %.2f) y:(%.2f %.2f) z:(%.2f %.2f)\n", res->minX, res->maxX, res->minY, res->maxY, res->minZ, res->maxZ);
	return res;
}

HPCD* HPCD_InitFromPoints(std::vector<Point> *points, float resolution) {
	std::vector<float> float_data;
	std::vector<unsigned char> color_data;
	for (size_t i=0;i<points->size();i++) {
		float_data.push_back(points->at(i).x);
		float_data.push_back(points->at(i).y);
		float_data.push_back(points->at(i).z);
		color_data.push_back(points->at(i).r);
		color_data.push_back(points->at(i).g);
		color_data.push_back(points->at(i).b);
	}
	return HPCD_InitFromVector(&float_data, &color_data, resolution);
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        printf("get_accuracy ground_truth.ply prediction.ply\n");
        exit(1);
    }

    std::vector<Point> gt_points;
    loadPLY(argv[1], &gt_points);
    std::vector<Point> pt_points;
    loadPLY(argv[2], &pt_points);

    //randomly shuffle points so that voxels can be sampled non-deterministically
    std::srand(0);
    std::random_shuffle ( gt_points.begin(), gt_points.end() );
    std::random_shuffle ( pt_points.begin(), pt_points.end() );

    float resolution = 0.05;
	bool use_default_err = true;
	float default_pos_err = resolution * sqrt(3) * 3;
	float default_col_err = 3;
    HPCD* gtv = HPCD_InitFromPoints(&gt_points, resolution);
    HPCD* ptv = HPCD_InitFromPoints(&pt_points, resolution);

    float position_rmse = 0.0;
    float color_rmse = 0.0;
    int common_voxels = 0;
    std::vector<Point> output;

	for (int i = 0; i<gtv->maxSize; i++) {
		HPoint* g = gtv->data[i];
        if (!g)
            continue;
        int pid = HPCD_find(ptv, g->xi, g->yi, g->zi); 
        if (pid >= 0) {
            HPoint* p = ptv->data[pid];
            common_voxels += 1;
            position_rmse += (g->x - p->x) * (g->x - p->x);
            position_rmse += (g->y - p->y) * (g->y - p->y);
            position_rmse += (g->z - p->z) * (g->z - p->z);
            color_rmse += (g->r/255.0 - p->r/255.0) * (g->r/255.0 - p->r/255.0);
            color_rmse += (g->g/255.0 - p->g/255.0) * (g->g/255.0 - p->g/255.0);
            color_rmse += (g->b/255.0 - p->b/255.0) * (g->b/255.0 - p->b/255.0);

            Point o = { g->x, g->y, g->z, 0,255,0 };
            output.push_back(o);
        } else {
			if (use_default_err) {
				position_rmse += default_pos_err;
				color_rmse += default_col_err;
			}
            Point o = { g->x, g->y, g->z, 0,0,255 };
            output.push_back(o);
        }
    }

	for (int i = 0; i<ptv->maxSize; i++) {
		HPoint* p = ptv->data[i];
        if (!p)
            continue;
        int gid = HPCD_find(gtv, p->xi, p->yi, p->zi); 
        if (gid < 0) {
            Point o = { p->x, p->y, p->z, 255,0,0 };
            output.push_back(o);
        }
    }
//    writePLY("tmp.ply", &output);

//    printf("common_voxels %d\n", common_voxels);
    float voxel_precision = 1.0 * common_voxels / ptv->numPoints;
    float voxel_recall = 1.0 * common_voxels / gtv->numPoints;
    float F1_score = 2*voxel_precision*voxel_recall/(voxel_precision + voxel_recall);
//    printf("voxel_precision: %.3f\n", voxel_precision);
//    printf("voxel_recall: %.3f\n", voxel_recall);
//    printf("F1_score: %.3f\n", F1_score);

	if (use_default_err) {
		position_rmse = sqrt(position_rmse / gtv->numPoints / 3);
		color_rmse = sqrt(color_rmse / gtv->numPoints / 3);
	} else {
		position_rmse = sqrt(position_rmse / common_voxels / 3);
		color_rmse = sqrt(color_rmse / common_voxels / 3);
	}
//    printf("position_rmse: %.3f\n", position_rmse);
//    printf("color_rmse: %.3f\n", color_rmse);
    printf("%.3f, %.3f, %.3f, %.3f, %.3f\n", voxel_precision, voxel_recall, F1_score, position_rmse, color_rmse);
}
