function output_note = PCDtoBIN_v2()

% this code is taken and modified from Mikaela Angelina Uy's PointNetVLAD

%pc_output_folder="F:\aashr\Documents\New Submaps WithHolo\Bin_Submaps_matlab\";
%pc_output_folder="F:\aashr\Documents\New Submaps WithHolo\Bin_submaps_10m_0.5m_filteredGround&Ceiling\";
for i=1:20

    pc_output_folder="E:\Link Lab Data\with floor and cieling\6X6\Trainset_bin\"+ num2str(i) +"\bin_submaps_6m_1m\";
    csv_path="E:\Link Lab Data\with floor and cieling\6X6\Trainset_bin\"+ num2str(i) +"\";
    mkdir(pc_output_folder);
    csv_file_name= 'Origin_Centroids.csv';
    fid_locations=fopen(strcat(csv_path,csv_file_name), 'w');
    fprintf(fid_locations,'%s,%s,%s,%s\n','number','x','y','z');
    
    % run(strcat("E:\Link Lab Data\Trainset\5\bin_submaps_10m_1m\",'scale_size_2.m'));
    
    % scale_size_vec_sol = scale_size_vec;
    
    %PCDFolder = 'D:\PCD_Files_Submaps';
    PCDFolder = "E:\Link Lab Data\with floor and cieling\6X6\Trainset\"+ num2str(i) +"\submaps_6m_1m";
    filePattern = fullfile(PCDFolder, '*.pcd');
    pcdFiles   = dir(filePattern);
    scale_size_vec = [];
    
    %scale_size=0.120;
    for k = 1:length(pcdFiles)
        %   scale_size = scale_size_vec_sol(k,2);
        baseFileName = pcdFiles(k).name;
        splitted = split(baseFileName);
        testsplit = split(baseFileName, ".");
        disp(testsplit(1));
        %num= split(splitted(2,1),".");
        %disp(num(1,1));
        fprintf('%s\n',baseFileName);
        fullFileName = fullfile(PCDFolder, baseFileName);
        fprintf('Now reading %s\n', fullFileName);
        
        ptcloud  = pcread(fullFileName);
        disp(ptcloud);
        initial_size = ptcloud.Count();
        %   scale_size = 0.064948 + 0.084425 *(initial_size)^(1/3)/100
        %   scale_size = 0.13775  +1.43e-08 *(initial_size)
        
        
        
        % ptcloud  = pcread("D:\PCD_Files_Submaps\Submap 21.pcd");
        % disp(class(ptcloud));
        % disp(ptcloud);
        % disp(length(ptcloud));
        %disp(out_of_plane)
        %out_of_plane = ptcloud;
        % disp(out_of_plane);
        % x = ptcloud(:,:,1);
        % y = ptcloud(:,:,2);
        % z = ptcloud(:,:,3);
        % out_of_plane = [x(:)'; y(:)', z(:)'];
        %pcshow(out_of_plane);
        %out_of_plane = pointCloud(xyz);
        %disp(out_of_plane);
        target_pc_size=4096;
        scale_size=0.200;
        
        downsampled=pcdownsample(ptcloud,'gridAverage',scale_size);
        iteration = 0;
        while (downsampled.Count()<target_pc_size)
            scale_size=scale_size-0.005;
            if(scale_size<=0)
                fprintf('iteration 1&2 is: %d \n',iteration);
                xyz=ptcloud.Location;
                break;
            end
            downsampled=pcdownsample(ptcloud,'gridAverage',scale_size);
            iteration = iteration + 1;
        end
        
        while (downsampled.Count()>target_pc_size)
            scale_size=scale_size+0.005;
            downsampled=pcdownsample(ptcloud,'gridAverage',scale_size);
            iteration = iteration + 1;
        end
        
        fprintf('iteration 1&2 is: %d \n',iteration);
        fprintf('final scale %d \n',scale_size);
        if(scale_size>0)
            xyz=[downsampled.Location(:,1),downsampled.Location(:,2),downsampled.Location(:,3)];
        end
        
        %add additional random points
        num_extra_points=target_pc_size-size(xyz,1);
        %disp(size(xyz,1));
        disp(num_extra_points);
        disp(length(ptcloud));
        permutation=randperm(length(ptcloud.Location));
        disp(length(permutation));
        
        disp(size(permutation));
        %disp(permutation);
        try
            sample_out=permutation(1:num_extra_points);
        catch
            warning('number of extra points exceeded permutation.');
            continue;
        end
        sample=ptcloud.Location(sample_out,:);%3xn
        
        output=[xyz',sample'];
        %output = output';
        x_cen=mean(output(1,:));
        y_cen=mean(output(2,:));
        z_cen=mean(output(3,:));
        centroid=[x_cen;y_cen;z_cen;1];
        %centroid_g=double(laser_global_poses{frame_start})*double(centroid);
        
        %make spread s=0.5/d
        sum=0;
        for i=1:size(output,2)
            sum=sum+sqrt((output(1,i)-x_cen)^2+(output(2,i)-y_cen)^2+(output(3,i)-z_cen)^2);
        end
        d=sum/size(output,2);
        s=0.5/d;
        
        T=[[s,0,0,-s*(x_cen)];...
            [0,s,0,-s*(y_cen)];...
            [0,0,s,-s*(z_cen)];...
            [0,0,0,1]];
        scaled_output=T*[output; ones(1, size(output,2))];
        scaled_output=-scaled_output;
        
        %Enforce to be in [-1,1] and have exactly target_pc_size points
        cleaned=[];
        for i=1:size(scaled_output,2)
            if(scaled_output(1,i)>=-1 && scaled_output(1,i)<=1 && scaled_output(2,i)>=-1 && scaled_output(2,i)<=1 ...
                    && scaled_output(3,i)>=-1 && scaled_output(3,i)<=1)
                cleaned=[cleaned,scaled_output(:,i)];
            end
        end
        
        %make number of points equal to target_pc_size
        num_extra_points=target_pc_size-size(cleaned,2);
        disp(strcat(num2str(size(cleaned,2)),'.',num2str(num_extra_points)));
        permutation=randperm(length(ptcloud.Location));
        i=1;
        iteration3 = 0;
        while size(cleaned,2)<target_pc_size
            try
                new_point=-T*[ptcloud.Location(:,permutation(1,i));1];
                if(new_point(1,1)>=-1 && new_point(1,1)<=1 && new_point(2,1)>=-1 && new_point(2,1)<=1 ...
                        && new_point(3,1)>=-1 && new_point(3,1)<=1)
                    cleaned=[cleaned,new_point];
                end
                i=i+1;
            catch
                warning('Problem in size of the pcd file. For small number of original points.');
                break;
            end
            iteration3 = iteration3 + 1;
            
        end
        
        fprintf('iteration 3 is: %d \n',iteration3);
        
        cleaned=cleaned(1:3,:);
        
        if(size(cleaned,2)~=target_pc_size)
            disp('Invalid pointcloud ')
            
            continue;
        end
        
        fileID = fopen(strcat(pc_output_folder, testsplit(1),'.bin'),'w');
        fwrite(fileID,cleaned,'double');
        fclose(fileID);
        %             disp(num2str(origin_timestamp));
        %             disp(fid_locations(1));
        x = cell2mat(testsplit(1));
        
        fprintf(fid_locations, '%s,%f,%f,%f\n',x, centroid(1,1), centroid(2,1), centroid(3,1));
        %             dlmwrite(fid_locations, M, '-append');
        
        scale_size_vec = [scale_size_vec ; [initial_size/10^6, scale_size]];
        %             disp(scale_size_vec);
        
        
        
    end
    disp(size(scale_size_vec));
    fclose(fid_locations);
    matlab.io.saveVariablesToScript(strcat(pc_output_folder,'scale_size_2.m'),'scale_size_vec');
    output_note = 'Bin file created from MATLAB code';
end
            %disp(cleaned);
             %pcshow(cleaned')
            %pcwrite(pointCloud(cleaned'), "D:\Matlab_downsapmled_3.pcd")
%             fileID = fopen('D:\binsubmap3.bin','w');
%             fwrite(fileID,cleaned,'double');
%             fclose(fileID);